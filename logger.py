import logging

class LoggerFactory:
    @classmethod
    def get_logger(cls, name: str, level: int = logging.DEBUG) -> logging.Logger:
        """获取一个具有统一配置的logger，同时允许requests日志显示"""
        # 先配置 root logger（这样能捕获 requests 日志）
        root_logger = logging.getLogger()
        root_logger.setLevel(level)  # 设置成 DEBUG

        # 再配置你的命名 logger
        logger = logging.getLogger(name)
        logger.setLevel(level)  # 你的 logger 可以更详细

        # 避免重复添加 handler
        if not root_logger.handlers:
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter(
                '[%(levelname)s] %(asctime)s - %(name)s - %(message)s'
            )
            ch.setFormatter(formatter)
            root_logger.addHandler(ch)  # 让 root logger 处理所有日志

        return logger
