"""
Git 仓库同步服务
用于从 Git 仓库同步技能文件
"""
import os
import re
import json
import yaml
import shutil
import subprocess
import stat
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from flask import current_app

from app import db
from app.models.skill_repository import SkillRepository, GitSkill, SkillSyncLog, GitCredential
from app.utils.crypto import decrypt_data


class GitSyncService:
    """Git仓库同步服务"""

    # 支持的技能文件扩展名
    SUPPORTED_EXTENSIONS = ['.py', '.js', '.yaml', '.yml', '.json']

    def __init__(self):
        """初始化同步服务"""
        self.git_repos_dir = current_app.config.get('GIT_REPOS_DIR', 'git_repos')
        # 确保目录存在
        os.makedirs(self.git_repos_dir, exist_ok=True)

    def sync(self, repository_id: int, sync_type: str = 'manual', triggered_by: str = None) -> Dict:
        """
        同步仓库

        Args:
            repository_id: 仓库ID
            sync_type: 同步类型 (manual, scheduled, webhook)
            triggered_by: 触发人/触发源

        Returns:
            Dict: 同步结果
        """
        repository = SkillRepository.query.get(repository_id)
        if not repository:
            return {'success': False, 'error': '仓库不存在'}

        # 创建同步日志
        sync_log = SkillSyncLog(
            repository_id=repository_id,
            sync_type=sync_type,
            status='running',
            triggered_by=triggered_by or 'system'
        )
        db.session.add(sync_log)
        db.session.commit()

        # 更新仓库状态
        repository.status = 'syncing'
        db.session.commit()

        try:
            start_time = datetime.utcnow()

            # 克隆或拉取仓库
            repo_path, commit_info = self._clone_or_pull(repository)

            # 解析技能文件
            skills = self._parse_skills(repository, repo_path)

            # 同步到数据库
            stats = self._sync_skills_to_db(repository, skills)

            # 更新同步日志
            sync_log.status = 'success'
            sync_log.skills_added = stats['added']
            sync_log.skills_updated = stats['updated']
            sync_log.skills_deleted = stats['deleted']
            sync_log.completed_at = datetime.utcnow()
            sync_log.duration = (sync_log.completed_at - start_time).total_seconds()
            sync_log.git_commit_hash = commit_info.get('hash')
            sync_log.git_commit_message = commit_info.get('message')

            # 更新仓库状态
            repository.status = 'success'
            repository.last_sync_at = datetime.utcnow()
            repository.last_sync_status = 'success'
            repository.last_sync_message = '同步成功'
            repository.skills_count = GitSkill.query.filter_by(repository_id=repository_id).count()

            db.session.commit()

            return {
                'success': True,
                'stats': stats,
                'commit_info': commit_info
            }

        except Exception as e:
            # 更新同步日志
            sync_log.status = 'error'
            sync_log.error_message = str(e)
            sync_log.completed_at = datetime.utcnow()

            # 更新仓库状态
            repository.status = 'error'
            repository.last_sync_status = 'error'
            repository.last_sync_message = str(e)

            db.session.commit()

            return {
                'success': False,
                'error': str(e)
            }

    def _clone_or_pull(self, repository: SkillRepository) -> Tuple[str, Dict]:
        """
        克隆或拉取仓库

        Args:
            repository: 仓库对象

        Returns:
            Tuple[str, Dict]: (仓库路径, commit信息)
        """
        repo_path = os.path.join(self.git_repos_dir, f'repo_{repository.id}')

        # 构建带认证的URL
        git_url, ssh_config = self._build_authenticated_url(repository)

        if os.path.exists(repo_path):
            # 拉取更新
            self._pull_repo(repo_path, git_url, repository.branch, ssh_config)
        else:
            # 克隆仓库
            self._clone_repo(git_url, repo_path, repository.branch, ssh_config)

        # 获取最新commit信息
        commit_info = self._get_commit_info(repo_path, repository.branch)

        return repo_path, commit_info

    def _build_authenticated_url(self, repository: SkillRepository) -> Tuple[str, dict]:
        """
        构建带认证的Git URL

        Args:
            repository: 仓库对象

        Returns:
            Tuple[str, dict]: (认证的URL, SSH配置信息)
        """
        git_url = repository.git_url
        ssh_config = {'is_ssh': False, 'key_path': None}

        if repository.auth_type == 'public':
            return git_url, ssh_config

        elif repository.auth_type == 'token':
            if not repository.git_credential_id:
                current_app.logger.warning(f'Repository {repository.id} has auth_type=token but no credential_id')
                return git_url, ssh_config
            credential = GitCredential.query.get(repository.git_credential_id)
            if credential and credential.github_token:
                try:
                    token = decrypt_data(credential.github_token)
                    # 将token插入URL
                    # https://github.com/user/repo.git -> https://token@github.com/user/repo.git
                    if git_url.startswith('https://'):
                        git_url = git_url.replace('https://', f'https://{token}@')
                    elif git_url.startswith('http://'):
                        git_url = git_url.replace('http://', f'http://{token}@')
                except Exception as e:
                    current_app.logger.error(f'Failed to decrypt token for repository {repository.id}: {e}')
            return git_url, ssh_config

        elif repository.auth_type == 'ssh_key':
            if not repository.git_credential_id:
                current_app.logger.warning(f'Repository {repository.id} has auth_type=ssh_key but no credential_id')
                return git_url, ssh_config
            # SSH认证通过环境变量处理
            credential = GitCredential.query.get(repository.git_credential_id)
            if credential and credential.ssh_key_content:
                try:
                    # 创建临时SSH密钥文件
                    ssh_dir = os.path.join(self.git_repos_dir, '.ssh')
                    os.makedirs(ssh_dir, exist_ok=True)
                    ssh_key_path = os.path.join(ssh_dir, f'repo_{repository.id}')

                    # 写入SSH密钥
                    with open(ssh_key_path, 'w') as f:
                        f.write(decrypt_data(credential.ssh_key_content))
                    os.chmod(ssh_key_path, 0o600)

                    ssh_config = {'is_ssh': True, 'key_path': ssh_key_path}
                except Exception as e:
                    current_app.logger.error(f'Failed to setup SSH key for repository {repository.id}: {e}')

            return git_url, ssh_config

        return git_url, ssh_config

    def _clone_repo(self, git_url: str, repo_path: str, branch: str = 'main', ssh_config: dict = None):
        """克隆仓库"""
        cmd = ['git', 'clone', '--depth', '1', '--branch', branch, git_url, repo_path]

        env = os.environ.copy()

        # 配置SSH认证
        if ssh_config and ssh_config.get('is_ssh') and ssh_config.get('key_path'):
            ssh_key_path = ssh_config['key_path']
            if os.path.exists(ssh_key_path):
                env['GIT_SSH_COMMAND'] = f'ssh -i {ssh_key_path} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Git clone failed: {e.stderr}')

    def _pull_repo(self, repo_path: str, git_url: str, branch: str = 'main', ssh_config: dict = None):
        """拉取更新"""
        env = os.environ.copy()

        # 配置SSH认证
        if ssh_config and ssh_config.get('is_ssh') and ssh_config.get('key_path'):
            ssh_key_path = ssh_config['key_path']
            if os.path.exists(ssh_key_path):
                env['GIT_SSH_COMMAND'] = f'ssh -i {ssh_key_path} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null'

        try:
            cmd = ['git', 'fetch', 'origin', branch]
            subprocess.run(cmd, cwd=repo_path, env=env, check=True, capture_output=True, text=True)

            cmd = ['git', 'checkout', branch]
            subprocess.run(cmd, cwd=repo_path, check=True, capture_output=True, text=True)

            cmd = ['git', 'reset', '--hard', f'origin/{branch}']
            subprocess.run(cmd, cwd=repo_path, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            raise Exception(f'Git pull failed: {e.stderr}')

    def _get_commit_info(self, repo_path: str, branch: str) -> Dict:
        """获取commit信息"""
        try:
            # 获取commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_hash = result.stdout.strip() if result.stdout else ''

            # 获取commit message
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%B'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_message = result.stdout.strip() if result.stdout else ''

            # 获取commit author
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%an'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_author = result.stdout.strip() if result.stdout else ''

            # 获取commit date
            result = subprocess.run(
                ['git', 'log', '-1', '--pretty=%ci'],
                cwd=repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            commit_date_str = result.stdout.strip() if result.stdout else ''

            try:
                commit_date = datetime.strptime(commit_date_str, '%Y-%m-%d %H:%M:%S %z')
                # 转换为UTC并去掉时区信息
                commit_date = commit_date.replace(tzinfo=None)
            except:
                commit_date = datetime.utcnow()

            return {
                'hash': commit_hash,
                'message': commit_message,
                'author': commit_author,
                'date': commit_date
            }
        except subprocess.CalledProcessError as e:
            # Git命令失败，返回默认值
            current_app.logger.error(f'Failed to get commit info: {e.stderr if e.stderr else str(e)}')
            return {
                'hash': '',
                'message': '',
                'author': '',
                'date': datetime.utcnow()
            }
        except Exception as e:
            # 其他错误，返回默认值
            current_app.logger.error(f'Error getting commit info: {str(e)}')
            return {
                'hash': '',
                'message': '',
                'author': '',
                'date': datetime.utcnow()
            }

    def _parse_skills(self, repository: SkillRepository, repo_path: str) -> List[Dict]:
        """
        解析技能目录 - 参考 Claude Code Skills 格式

        每个目录代表一个技能，SKILL.md 包含技能信息

        目录结构:
        skills/
        ├── pdf/
        │   ├── SKILL.md
        │   ├── extract_text.py
        │   └── templates/
        │       └── summary.html
        └── csv/
            ├── SKILL.md
            └── analyze.py

        Args:
            repository: 仓库对象
            repo_path: 仓库路径

        Returns:
            List[Dict]: 技能列表
        """
        skills = []
        skills_path = os.path.join(repo_path, repository.skills_path.lstrip('/'))

        if not os.path.exists(skills_path):
            current_app.logger.warning(f'技能路径不存在: {skills_path}')
            return skills

        # 遍历技能路径下的直接子目录（每个目录代表一个技能）
        try:
            for item in sorted(os.listdir(skills_path)):
                item_path = os.path.join(skills_path, item)

                # 只处理目录，跳过文件
                if not os.path.isdir(item_path):
                    continue

                # 跳过隐藏目录
                if item.startswith('.'):
                    continue

                # 解析技能目录
                skill = self._parse_skill_directory(repository, item, item_path, repo_path)
                if skill:
                    skills.append(skill)

        except Exception as e:
            current_app.logger.error(f'遍历技能目录失败: {str(e)}')

        current_app.logger.info(f'成功解析 {len(skills)} 个技能')
        return skills

    def _parse_skill_directory(self, repository: SkillRepository, skill_dir_name: str, skill_dir_path: str, repo_path: str) -> Optional[Dict]:
        """
        解析单个技能目录 - 参考 Claude Code Skills 格式

        SKILL.md 格式:
        ---
        name: pdf
        description: Extract and analyze text from PDF documents. Use when users ask to process or read PDFs.
        ---

        # PDF Processing Skill

        Use the extract_text.py script in this folder to extract text from PDFs...

        Args:
            repository: 仓库对象
            skill_dir_name: 技能目录名
            skill_dir_path: 技能目录完整路径
            repo_path: 仓库根路径

        Returns:
            Optional[Dict]: 技能信息
        """
        try:
            # 优先查找 SKILL.md（Claude Code 标准）
            skill_md_files = ['SKILL.md', 'skill.md']
            skill_md_path = None

            for md_file in skill_md_files:
                test_path = os.path.join(skill_dir_path, md_file)
                if os.path.exists(test_path):
                    skill_md_path = test_path
                    break

            # 默认技能信息
            skill_info = {
                'name': skill_dir_name,
                'code': skill_dir_name.lower().replace('-', '_').replace(' ', '_'),
                'description': f'The {skill_dir_name} skill',
                'script_content': '',
                'script_type': 'markdown',
                'params_schema': None,
                'file_path': os.path.relpath(skill_dir_path, repo_path).replace('\\', '/')
            }

            if skill_md_path:
                # 读取 SKILL.md 文件
                with open(skill_md_path, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                # 提取 YAML front matter 和描述
                metadata = self._extract_skill_metadata(md_content)
                skill_info.update(metadata)

                # 完整的 SKILL.md 内容作为技能内容
                skill_info['script_content'] = md_content
                skill_info['script_type'] = 'markdown'

                current_app.logger.info(f'解析技能: {skill_info["name"]} - {skill_info["description"][:50]}...')
            else:
                # 没有 SKILL.md，尝试找其他脚本文件
                script_file = self._find_script_file(skill_dir_path)
                if script_file:
                    with open(script_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    file_ext = os.path.splitext(script_file)[1].lower()
                    skill_info['script_content'] = content
                    skill_info['script_type'] = self._get_script_type(file_ext)

                    # 尝试从脚本文件提取元数据
                    metadata = self._extract_metadata(content, file_ext)
                    if metadata.get('name'):
                        skill_info.update(metadata)

                    current_app.logger.info(f'解析技能(从脚本): {skill_info["name"]}')
                else:
                    current_app.logger.warning(f'跳过技能目录 {skill_dir_name}: 没有 SKILL.md 或支持的脚本文件')
                    return None

            return skill_info

        except Exception as e:
            current_app.logger.warning(f'解析技能目录失败 {skill_dir_path}: {str(e)}')
            return None

    def _find_script_file(self, skill_dir_path: str) -> Optional[str]:
        """
        在技能目录中查找脚本文件

        Args:
            skill_dir_path: 技能目录路径

        Returns:
            Optional[str]: 脚本文件路径
        """
        # 优先级顺序：.py > .js > .yaml > .yml > .json
        for ext in ['.py', '.js', '.yaml', '.yml', '.json']:
            for filename in os.listdir(skill_dir_path):
                if filename.endswith(ext):
                    return os.path.join(skill_dir_path, filename)
        return None

    def _extract_skill_metadata(self, md_content: str) -> Dict:
        """
        从 skill.md 中提取技能元数据

        支持格式：
        ---
        name: skill-name
        description: Skill description
        ---

        Args:
            md_content: Markdown 文件内容

        Returns:
            Dict: 元数据
        """
        metadata = {}

        # 尝试提取 YAML front matter
        front_matter = self._extract_front_matter(md_content)

        if front_matter and isinstance(front_matter, dict):
            # 从 front matter 提取字段
            if front_matter.get('name'):
                metadata['name'] = front_matter.get('name')
                # 如果没有 code 字段，从 name 生成
                if front_matter.get('code'):
                    metadata['code'] = front_matter.get('code')
                else:
                    metadata['code'] = front_matter.get('name').lower().replace('-', '_').replace(' ', '_')
            if front_matter.get('description'):
                metadata['description'] = front_matter.get('description')

            # 处理参数定义
            params = front_matter.get('parameters')
            if params:
                metadata['params_schema'] = json.dumps(params, ensure_ascii=False)
        else:
            # 没有 front matter，尝试从 Markdown 内容中提取
            lines = md_content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('# '):
                    metadata['name'] = line[2:].strip()
                    metadata['code'] = metadata['name'].lower().replace('-', '_').replace(' ', '_')
                    break

            # 如果没有找到描述，使用前几行非标题内容
            if not metadata.get('description'):
                desc_lines = []
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        desc_lines.append(line)
                        if len(desc_lines) >= 3:
                            break
                metadata['description'] = ' '.join(desc_lines)[:200] if desc_lines else ''

        return metadata

    def _get_script_type(self, file_ext: str) -> str:
        """获取脚本类型"""
        type_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json'
        }
        return type_map.get(file_ext, 'unknown')

    def _extract_metadata(self, content: str, file_ext: str) -> Dict:
        """
        从文件内容中提取元数据

        Args:
            content: 文件内容
            file_ext: 文件扩展名

        Returns:
            Dict: 元数据
        """
        metadata = {}

        if file_ext in ['.yaml', '.yml']:
            # YAML格式，整个文件就是技能定义
            try:
                data = yaml.safe_load(content)
                if isinstance(data, dict):
                    metadata['name'] = data.get('name', metadata.get('name'))
                    metadata['code'] = data.get('code', metadata.get('code'))
                    metadata['description'] = data.get('description', '')
                    metadata['params_schema'] = json.dumps(data.get('parameters')) if data.get('parameters') else None
            except:
                pass

        elif file_ext == '.json':
            # JSON格式
            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    metadata['name'] = data.get('name', metadata.get('name'))
                    metadata['code'] = data.get('code', metadata.get('code'))
                    metadata['description'] = data.get('description', '')
                    metadata['params_schema'] = json.dumps(data.get('parameters')) if data.get('parameters') else None
            except:
                pass

        elif file_ext in ['.py', '.js']:
            # 从注释中提取YAML front matter
            front_matter = self._extract_front_matter(content)
            if front_matter:
                metadata['name'] = front_matter.get('name', metadata.get('name'))
                metadata['code'] = front_matter.get('code', metadata.get('code'))
                metadata['description'] = front_matter.get('description', '')
                metadata['params_schema'] = json.dumps(front_matter.get('parameters')) if front_matter.get('parameters') else None

        return metadata

    def _extract_front_matter(self, content: str) -> Optional[Dict]:
        """
        提取YAML front matter

        Args:
            content: 文件内容

        Returns:
            Optional[Dict]: front matter数据
        """
        # 匹配 --- 分隔的YAML front matter
        pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(pattern, content, re.DOTALL)

        if match:
            try:
                return yaml.safe_load(match.group(1))
            except:
                pass

        return None

    def _sync_skills_to_db(self, repository: SkillRepository, skills: List[Dict]) -> Dict:
        """
        同步技能到数据库

        Args:
            repository: 仓库对象
            skills: 技能列表

        Returns:
            Dict: 统计信息
        """
        stats = {'added': 0, 'updated': 0, 'deleted': 0}

        # 获取当前数据库中的技能
        existing_skills = {
            skill.file_path: skill
            for skill in GitSkill.query.filter_by(repository_id=repository.id).all()
        }

        # 当前同步的技能路径集合
        current_paths = {skill['file_path'] for skill in skills}

        # 更新或添加技能
        for skill_data in skills:
            existing_skill = existing_skills.get(skill_data['file_path'])

            if existing_skill:
                # 更新现有技能
                existing_skill.name = skill_data['name']
                existing_skill.code = skill_data['code']
                existing_skill.description = skill_data['description']
                existing_skill.script_content = skill_data['script_content']
                existing_skill.script_type = skill_data['script_type']
                existing_skill.params_schema = skill_data['params_schema']
                existing_skill.file_path = skill_data['file_path']
                existing_skill.updated_at = datetime.utcnow()
                stats['updated'] += 1
            else:
                # 添加新技能
                new_skill = GitSkill(
                    repository_id=repository.id,
                    name=skill_data['name'],
                    code=skill_data['code'],
                    description=skill_data['description'],
                    script_content=skill_data['script_content'],
                    script_type=skill_data['script_type'],
                    params_schema=skill_data['params_schema'],
                    file_path=skill_data['file_path']
                )
                db.session.add(new_skill)
                stats['added'] += 1

        # 删除不再存在的技能
        for file_path, skill in existing_skills.items():
            if file_path not in current_paths:
                db.session.delete(skill)
                stats['deleted'] += 1

        db.session.commit()

        return stats

    def _remove_readonly(self, func, path, excinfo):
        """
        Windows专用的错误处理函数：移除只读属性后重试删除
        """
        if not os.access(path, os.W_OK):
            # 尝试移除只读属性
            os.chmod(path, stat.S_IWUSR)
            func(path)
        else:
            # 如果仍然失败，直接raise
            raise

    def delete_repo_files(self, repository_id: int):
        """
        删除仓库文件

        Args:
            repository_id: 仓库ID
        """
        repo_path = os.path.join(self.git_repos_dir, f'repo_{repository_id}')
        if os.path.exists(repo_path):
            try:
                # Windows兼容：使用onerror处理只读文件
                shutil.rmtree(repo_path, onerror=self._remove_readonly)
            except Exception as e:
                current_app.logger.warning(f'标准删除失败，尝试强制删除: {str(e)}')
                # 如果仍然失败，尝试更激进的方法
                time.sleep(0.5)  # 等待文件句柄释放
                try:
                    shutil.rmtree(repo_path, onerror=self._remove_readonly)
                except Exception as e2:
                    current_app.logger.error(f'删除仓库文件失败: {str(e2)}')
                    raise

        # 删除SSH密钥
        ssh_key_path = os.path.join(self.git_repos_dir, '.ssh', f'repo_{repository_id}')
        if os.path.exists(ssh_key_path):
            try:
                os.remove(ssh_key_path)
            except Exception as e:
                current_app.logger.warning(f'删除SSH密钥失败: {str(e)}')


# 全局实例
_git_sync_service = None


def get_git_sync_service():
    """获取Git同步服务实例"""
    global _git_sync_service
    if _git_sync_service is None:
        _git_sync_service = GitSyncService()
    return _git_sync_service
