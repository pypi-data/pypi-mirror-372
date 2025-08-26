#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from .task_entity import BackoffType, ProcModeType, logger


@dataclass
class StorageConfig:
    """存储配置"""

    type: str = "redis"  # 存储类型：redis、mysql等
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None
    username: Optional[str] = None
    charset: str = "utf8mb4"

    # MySQL 特有配置
    database: Optional[str] = None
    table_prefix: Optional[str] = None

    @classmethod
    def from_dict(cls, config_dict: dict):
        storage_type = config_dict.get("type", "redis")

        # 基础配置
        config = {
            "type": storage_type,
            "host": config_dict.get("host", "localhost"),
            "password": config_dict.get("password"),
        }

        # 根据存储类型设置特定配置
        if storage_type == "redis":
            config.update(
                {"port": config_dict.get("port", 6379), "db": config_dict.get("db", 0)}
            )
        elif storage_type == "mysql":
            config.update(
                {
                    "port": config_dict.get("port", 3306),
                    "username": config_dict.get("username", "root"),
                    "database": config_dict.get("database", "123456"),
                    "charset": config_dict.get("charset", "utf8mb4"),
                    "table_prefix": config_dict.get("table_prefix", "tb_"),
                }
            )

        return cls(**config)

    def get_connection_info(self):
        """获取连接信息"""
        if self.type == "redis":
            return {
                "host": self.host,
                "port": self.port,
                "db": self.db,
                "password": self.password,
            }
        elif self.type == "mysql":
            return {
                "host": self.host,
                "port": self.port,
                "user": self.username,
                "password": self.password,
                "database": self.database,
                "charset": self.charset,
            }
        else:
            raise ValueError(f"不支持的存储类型: {self.type}")


@dataclass
class TaskConfig:
    """任务配置"""

    # 业务前缀
    biz_prefix: str = "default_biz_prefix"  # 业务redis队列的前缀

    # 执行配置
    batch_size: int = 50  # 批量处理数量

    # 重试配置
    max_retry_count: int = 3
    backoff_type: str = BackoffType.EXPONENTIAL.value  # fixed、linear、exponential
    backoff_interval: int = 10  # 基础间隔时间(秒)
    backoff_multiplier: float = 2.0  # 退避倍数

    # 资源配置
    min_gpu_memory_mb: int = 0  # 最小显存数量
    min_gpu_utilization: float = 0.0  # 最小显卡利用率

    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(
            biz_prefix=config_dict.get("biz_prefix", "default_biz_prefix"),
            batch_size=config_dict.get("batch_size", 50),
            max_retry_count=config_dict.get("max_retry_count", 3),
            backoff_type=config_dict.get("backoff_type", BackoffType.EXPONENTIAL.value),
            backoff_interval=config_dict.get("backoff_interval", 10),
            backoff_multiplier=config_dict.get("backoff_multiplier", 2.0),
            min_gpu_memory_mb=config_dict.get("min_gpu_memory_mb", 0),
            min_gpu_utilization=config_dict.get("min_gpu_utilization", 0.0),
        )


@dataclass
class ThreadPoolConfig:
    """线程池配置"""

    concurrency: int = 10
    proc_mode: str = ProcModeType.THREAD.value  # thread、process
    exec_timeout: int = 300  # 任务超时时间(秒)

    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(
            concurrency=config_dict.get("concurrency"),
            proc_mode=config_dict.get("proc_mode", ProcModeType.THREAD.value),
            exec_timeout=config_dict.get("exec_timeout", 300),
        )


@dataclass
class SchedulerConfig:
    """调度器配置"""

    cron: Optional[str] = None  # cron表达式
    interval: int = 10  # 间隔时间(秒)

    @classmethod
    def from_dict(cls, config_dict: dict):
        return cls(cron=config_dict.get("cron"), interval=config_dict.get("interval"))


@dataclass
class TaskBackoffConfig:
    """任务退避框架配置"""

    storage: StorageConfig = field(default_factory=StorageConfig)
    task: TaskConfig = field(default_factory=TaskConfig)
    threadpool: ThreadPoolConfig = field(default_factory=ThreadPoolConfig)
    scheduler: SchedulerConfig = field(default_factory=SchedulerConfig)

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "TaskBackoffConfig":
        """从字典创建配置"""
        storage_config = StorageConfig.from_dict(config_dict.get("storage", {}))
        task_config = TaskConfig.from_dict(config_dict.get("task", {}))
        threadpool_config = ThreadPoolConfig.from_dict(
            config_dict.get("threadpool", {})
        )
        scheduler_config = SchedulerConfig.from_dict(config_dict.get("scheduler", {}))

        return cls(
            storage=storage_config,
            task=task_config,
            threadpool=threadpool_config,
            scheduler=scheduler_config,
        )
