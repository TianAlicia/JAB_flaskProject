import os


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(24))

    # mysql 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = ""

    # redis配置
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379


class Development(BaseConfig):
    """开发配置"""

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/JAB_Project"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 默认日志等级
    # LOG_LEVEL = logging.DEBUG


class TestingConfig(BaseConfig):
    """测试配置"""

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # 内存数据库


class ProductionConfig(BaseConfig):
    """生成环境配置"""

    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1:3306/JAB_Project"
    SQLALCHEMY_TRACK_MODIFICATIONS = False


config = {
    "dev": Development,
    "test": TestingConfig,
    "prod": ProductionConfig,
}
