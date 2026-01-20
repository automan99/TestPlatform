"""
MCP Server 进程管理器
用于管理 stdio 类型的常驻进程
"""
import asyncio
import json
import logging
import subprocess
import threading
from typing import Dict, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProcessInfo:
    """进程信息"""
    mcp_id: int
    process: subprocess.Popen
    command: str
    args: list
    env: dict


class MCPProcessManager:
    """MCP Server 进程管理器（单例）"""

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._processes: Dict[int, ProcessInfo] = {}
        logger.info("MCP进程管理器初始化完成")

    def start_process(self, mcp_id: int, command: str, args: list, env: Optional[dict] = None) -> bool:
        """
        启动 MCP Server 进程

        Args:
            mcp_id: MCP Server ID
            command: 执行命令
            args: 命令参数
            env: 环境变量

        Returns:
            bool: 是否启动成功
        """
        # 如果进程已存在，先停止
        if mcp_id in self._processes:
            self.stop_process(mcp_id)

        try:
            # 构建完整命令
            full_command = [command] + args

            # 准备环境变量
            process_env = None
            if env:
                import os
                process_env = os.environ.copy()
                process_env.update(env)

            # 启动进程
            process = subprocess.Popen(
                full_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=process_env,
                text=False  # 使用字节模式，MCP使用JSON-RPC
            )

            # 保存进程信息
            self._processes[mcp_id] = ProcessInfo(
                mcp_id=mcp_id,
                process=process,
                command=command,
                args=args,
                env=env or {}
            )

            logger.info(f"MCP Server {mcp_id} 进程启动成功: PID={process.pid}")
            return True

        except Exception as e:
            logger.error(f"MCP Server {mcp_id} 进程启动失败: {e}", exc_info=True)
            return False

    def stop_process(self, mcp_id: int) -> bool:
        """
        停止 MCP Server 进程

        Args:
            mcp_id: MCP Server ID

        Returns:
            bool: 是否停止成功
        """
        if mcp_id not in self._processes:
            logger.warning(f"MCP Server {mcp_id} 进程不存在")
            return True

        try:
            process_info = self._processes[mcp_id]
            process = process_info.process

            # 尝试优雅终止
            process.terminate()

            # 等待进程结束（最多3秒）
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                # 强制终止
                process.kill()
                process.wait()

            # 清理资源
            if process.stdin:
                process.stdin.close()
            if process.stdout:
                process.stdout.close()
            if process.stderr:
                process.stderr.close()

            del self._processes[mcp_id]
            logger.info(f"MCP Server {mcp_id} 进程已停止")
            return True

        except Exception as e:
            logger.error(f"MCP Server {mcp_id} 进程停止失败: {e}", exc_info=True)
            # 即使出错也尝试清理
            if mcp_id in self._processes:
                del self._processes[mcp_id]
            return False

    def is_running(self, mcp_id: int) -> bool:
        """
        检查进程是否在运行

        Args:
            mcp_id: MCP Server ID

        Returns:
            bool: 是否正在运行
        """
        if mcp_id not in self._processes:
            return False

        process_info = self._processes[mcp_id]
        process = process_info.process

        # 检查进程是否还在运行
        return process.poll() is None

    def get_process_info(self, mcp_id: int) -> Optional[ProcessInfo]:
        """
        获取进程信息

        Args:
            mcp_id: MCP Server ID

        Returns:
            ProcessInfo: 进程信息，不存在则返回 None
        """
        return self._processes.get(mcp_id)

    def stop_all(self):
        """停止所有进程"""
        logger.info("正在停止所有 MCP Server 进程...")
        for mcp_id in list(self._processes.keys()):
            self.stop_process(mcp_id)
        logger.info("所有 MCP Server 进程已停止")

    def get_running_count(self) -> int:
        """获取运行中的进程数量"""
        count = 0
        for mcp_id, process_info in self._processes.items():
            if process_info.process.poll() is None:
                count += 1
        return count


# 全局单例
_mcp_process_manager = None


def get_mcp_process_manager() -> MCPProcessManager:
    """获取 MCP 进程管理器单例"""
    global _mcp_process_manager
    if _mcp_process_manager is None:
        _mcp_process_manager = MCPProcessManager()
    return _mcp_process_manager
