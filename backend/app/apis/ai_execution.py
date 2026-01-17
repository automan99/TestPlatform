"""
AI测试执行API
"""
from flask import request
from flask_restx import Namespace, Resource
from app.utils.errors import success_response, error_response
from app.models import TestCase, TestSuite, TestExecution, TestPlan, Project
from app import db
from datetime import datetime
import json
import random
import time

# 创建命名空间
ai_execution_ns = Namespace('ai-execution', description='AI测试执行接口')

# 存储执行状态（实际生产环境应该使用Redis或数据库）
execution_store = {}


@ai_execution_ns.route('/start')
class AIExecutionStartAPI(Resource):
    @ai_execution_ns.doc('start_ai_execution')
    def post(self):
        """启动AI测试执行"""
        try:
            data = request.get_json()
            case_ids = data.get('case_ids', [])
            environment_id = data.get('environment_id')

            if not case_ids:
                return error_response(message='请选择要执行的测试用例')

            # 生成执行ID
            execution_id = int(time.time() * 1000)

            # 获取测试用例信息
            test_cases = []
            for case_id in case_ids:
                case = TestCase.query.filter_by(id=case_id, is_deleted=False).first()
                if case:
                    test_cases.append({
                        'id': case.id,
                        'caseName': case.name,
                        'status': 'pending',
                        'progress': 0,
                        'currentStep': 0,
                        'totalSteps': 5,
                        'currentStepContent': '',
                        'errorInfo': '',
                        'logs': []
                    })

            # 初始化执行状态
            execution_store[execution_id] = {
                'execution_id': execution_id,
                'status': 'running',
                'test_cases': test_cases,
                'success_count': 0,
                'failed_count': 0,
                'skipped_count': 0,
                'start_time': datetime.utcnow().isoformat(),
                'environment_id': environment_id
            }

            # 启动后台模拟执行（实际应该使用Celery或类似任务队列）
            _simulate_execution(execution_id, case_ids)

            return success_response(data={
                'execution_id': execution_id,
                'message': 'AI执行已启动'
            })
        except Exception as e:
            return error_response(message=f'启动AI执行失败: {str(e)}')


@ai_execution_ns.route('/<int:execution_id>/status')
class AIExecutionStatusAPI(Resource):
    @ai_execution_ns.doc('get_execution_status')
    def get(self, execution_id):
        """获取执行状态"""
        try:
            if execution_id not in execution_store:
                return error_response(message='执行记录不存在', code=404)

            execution = execution_store.get(execution_id)

            return success_response(data=execution)
        except Exception as e:
            return error_response(message=f'获取执行状态失败: {str(e)}')


@ai_execution_ns.route('/<int:execution_id>/stop')
class AIExecutionStopAPI(Resource):
    @ai_execution_ns.doc('stop_execution')
    def post(self, execution_id):
        """停止执行"""
        try:
            if execution_id not in execution_store:
                return error_response(message='执行记录不存在', code=404)

            execution = execution_store[execution_id]
            execution['status'] = 'stopped'

            return success_response(message='已停止执行')
        except Exception as e:
            return error_response(message=f'停止执行失败: {str(e)}')


def _simulate_execution(execution_id, case_ids):
    """模拟AI执行过程（实际应该调用真实的AI Agent）"""
    import threading

    def execute():
        try:
            execution = execution_store.get(execution_id)
            if not execution:
                return

            test_cases = execution['test_cases']

            for index, case in enumerate(test_cases):
                # 检查是否已停止
                if execution_store.get(execution_id, {}).get('status') == 'stopped':
                    break

                # 更新状态为执行中
                case['status'] = 'running'
                case['currentStep'] = 1

                steps = [
                    '准备测试环境',
                    '解析测试步骤',
                    '执行测试操作',
                    '验证结果',
                    '生成测试报告'
                ]

                for step_index, step_name in enumerate(steps, 1):
                    # 检查是否已停止
                    if execution_store.get(execution_id, {}).get('status') == 'stopped':
                        break

                    case['currentStep'] = step_index
                    case['currentStepContent'] = step_name
                    case['progress'] = int((step_index / len(steps)) * 100)

                    # 添加日志
                    case['logs'].append({
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'level': 'INFO',
                        'message': f'正在执行: {step_name}'
                    })

                    # 模拟执行时间
                    time.sleep(random.uniform(1, 3))

                # 随机决定成功或失败
                if random.random() > 0.2:  # 80%成功率
                    case['status'] = 'completed'
                    execution['success_count'] += 1
                    case['logs'].append({
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'level': 'INFO',
                        'message': '测试执行成功'
                    })
                else:
                    case['status'] = 'failed'
                    execution['failed_count'] += 1
                    case['errorInfo'] = '断言失败: 期望值与实际值不匹配'
                    case['logs'].append({
                        'time': datetime.now().strftime('%H:%M:%S'),
                        'level': 'ERROR',
                        'message': '测试执行失败: 断言失败'
                    })

                # 保存执行记录到数据库
                try:
                    test_case = TestCase.query.get(case['id'])
                    if test_case:
                        execution_record = TestExecution(
                            test_case_id=case['id'],
                            status='passed' if case['status'] == 'completed' else 'failed',
                            executed_by='AI Agent',
                            actual_result=json.dumps({'logs': case['logs'][-5:]}),
                            duration=random.randint(10, 60)
                        )
                        db.session.add(execution_record)
                        db.session.commit()
                except Exception as e:
                    print(f'Save execution record failed: {e}')

            # 更新整体状态
            if execution_store.get(execution_id, {}).get('status') != 'stopped':
                execution['status'] = 'completed'

        except Exception as e:
            print(f'Execution failed: {e}')
            if execution_id in execution_store:
                execution_store[execution_id]['status'] = 'failed'

    # 在后台线程中执行
    thread = threading.Thread(target=execute)
    thread.daemon = True
    thread.start()
