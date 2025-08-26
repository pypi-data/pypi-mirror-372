#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务工作器模块
"""
import json
import logging
from concurrent.futures import TimeoutError as FutureTimeoutError
from typing import Optional, Dict, Any, Callable
from backoff.common.task_entity import TaskEntity
from .task_repository import TaskRepository
from backoff.models.backoff_threadpool import BackoffThreadPool
from backoff.common.result_entity import ResultEntity
from backoff.common.error_code import ErrorCode
from backoff.utils.gpu_utils import get_gpu_utils
from backoff.utils.serialize_data_utils import dumps_data, load_parse_params

logger = logging.getLogger()


def exec_task_in_process(task_handler: Callable, task_entity: "TaskEntity") -> Any:
    """
    进程池使用的可pickle顶层函数，仅负责调用业务handler。
    注意：禁止在子进程内访问不可序列化的状态（如锁、连接等）。
    """
    return task_handler(task_entity)


class BackoffWorker:
    """任务工作器，负责执行具体的任务"""

    def __init__(
        self,
        task_repository: TaskRepository,
        backoff_threadpool: Optional[BackoffThreadPool] = None,
        task_handler: Optional[Callable] = None,
        task_exception_handler: Optional[Callable] = None,
        task_timeout: int = 300,
    ):
        """
        初始化任务工作器

        Args:
            task_repository: 任务管理器
            backoff_threadpool: 线程池管理器
            task_handler: 任务处理函数
            task_timeout: 任务超时时间(秒)
        """
        self.task_repository = task_repository
        self.backoff_threadpool = backoff_threadpool
        self.task_handler = task_handler
        self.task_exception_handler = task_exception_handler
        self.task_timeout = task_timeout
        self.gpu_utils = get_gpu_utils()

    def execute_batch_tasks(self, pending_taskIds: list[str]) -> list[Dict[str, Any]]:
        """
        批量执行任务

        Args:
            tasks: 任务列表

        Returns:
            list[Dict[str, Any]]: 执行结果列表
        """

        if self.backoff_threadpool:
            # 执行结果集
            futures = []
            # 判断是否进程模式
            is_process_mode = self.backoff_threadpool.is_process_model()

            for taskId in pending_taskIds:
                task = self.task_repository.get_task(taskId)
                if not task:
                    continue
                valid_status = self.valid_task(task)
                if valid_status == False:
                    continue

                if is_process_mode:
                    self.task_repository.mark_task_processing(taskId)
                    future = self.backoff_threadpool.submit_task(exec_task_in_process, self.task_handler, task)
                else:
                    future = self.backoff_threadpool.submit_task(self.execute_task, task)

                futures.append((taskId, future, is_process_mode))

            # 收集结果
            for task_id, future, proc_mode in futures:
                try:
                    result = future.result(timeout=self.task_timeout)

                    if proc_mode:
                        # 子进程返回ResultEntity或兼容对象
                        # 兼容非ResultEntity返回
                        if result.success:
                            self.task_repository.mark_task_completed(
                                task_id, dumps_data(result.result)
                            )
                        else:
                            self.task_repository.mark_task_failed(
                                task_id,
                                dumps_data(result.message) + dumps_data(result.result),
                            )

                except Exception as e:

                    if isinstance(e, FutureTimeoutError):
                        logger.error(
                            f"任务 [{task_id}] 执行超时！超时时间：{self.task_timeout} 秒, 异常: {str(e)}"
                        )
                    else:
                        logger.error(f"任务 [{task_id}] 执行异常: {str(e)}")

                    if proc_mode:
                        # 异常时也要标记失败，并触发异常处理器
                        error_msg = f"execute_task 任务执行失败: {str(e)}"
                        self.task_repository.mark_task_failed(task_id, error_msg)
                        task_entity = self.task_repository.get_task(task_id)
                        self.execute_exception_handler(task_entity)

    def execute_task(self, task_entity: TaskEntity) -> Dict[str, Any]:
        """
        执行单个任务

        Args:
            task_entity: 任务实体

        Returns:
            Dict[str, Any]: 执行结果
        """

        task_id = task_entity.task_id
        task_params = json.loads(task_entity.param) if task_entity.param else {}

        try:
            self.task_repository.mark_task_processing(task_id)
            # 执行任务
            result_obj = self.execute_task_handler(task_entity)
            logger.info(f"任务 [{task_id}] 执行, 结果: {result_obj.success}")

            # 判断任务结果
            result_str = (
                json.dumps(result_obj.result)
                if isinstance(result_obj, (dict, list))
                else str(result_obj.result)
            )
            if not result_obj.success:
                self.task_repository.mark_task_failed(task_id, result_str)
                return ResultEntity.fail(
                    code=result_obj.code,
                    message=result_obj.message,
                    result=result_str,
                    task_id=task_id,
                )

            self.task_repository.mark_task_completed(task_id, result_str)
            return ResultEntity.ok(result_obj.result, task_id)

        except Exception as e:
            error_msg = f"execute_task 任务执行失败: {str(e)}"
            logger.error(f"任务 [{task_id}] , {error_msg}")
            self.task_repository.mark_task_failed(task_id, error_msg)

            # 如果有自定义异常处理器，则调用它
            if self.task_exception_handler:
                self.execute_exception_handler(task_entity)

            return ResultEntity.fail(
                ErrorCode.TASK_EXECUTE_FAILURE.code, error_msg, None, task_id
            )

    def valid_task(self, task_entity: TaskEntity) -> bool:
        """
        验证任务是否可以执行

        Args:
            task_entity: 任务实体

        Returns:
            bool: 是否可以执行
        """
        task_id = task_entity.task_id

        # 执行任务前先判断显存数和利用率是否满足要求,返回的是True 或者 False
        task_entity = self.task_repository.get_task(task_id)
        valid_status = self.gpu_utils.check_gpu_requirements(
            required_memory=task_entity.min_gpu_memory_mb,
            max_utilization=task_entity.min_gpu_utilization,
        )
        if valid_status == False:
            logger.info(f"任务 [{task_id}] 跳过执行，显存数和利用率不满足要求")
            return False

        # 如果有下次执行时间则判断是否到了执行时间
        if task_entity.next_execution_time > 0:
            if task_entity.is_ready_for_execution() == False:
                logger.debug(f"任务 [{task_id}] 跳过执行，未到执行时间")
                return False

        return True

    def execute_task_handler(self, task_entity: TaskEntity) -> Any:
        """使用自定义处理器执行任务"""
        try:
            return self.task_handler(task_entity)
        except Exception as e:
            raise e

    def execute_exception_handler(self, task_entity: TaskEntity) -> Any:
        """使用自定义异常处理器执行任务"""
        try:
            return self.task_exception_handler(task_entity)
        except Exception as e:
            raise e

    def set_custom_task_handler(self, handler: Callable):
        """
        设置任务处理器

        Args:
            handler: 任务处理函数
        """
        self.task_handler = handler
        logger.info(f"custom_task_handler: [{handler.__name__}] 任务处理器已设置")

    def set_custom_task_exception_handler(self, handler: Callable):
        """
        设置任务异常处理器

        Args:
            handler: 任务异常处理函数
        """
        self.task_exception_handler = handler
        logger.info(
            f"custom_task_exception_handler: [{handler.__name__}] 任务异常处理器已设置"
        )

    def get_queue_stats(self) -> Dict[str, int]:
        return self.task_repository.get_queue_stats()
