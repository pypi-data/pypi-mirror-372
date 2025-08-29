# src package

# 自动应用日志配置
try:
    from .config.logging_config import setup_logging
    setup_logging()
except Exception:
    # 如果日志配置失败，使用基本配置，避免阻塞应用启动
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
