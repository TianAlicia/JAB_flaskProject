from flask import Flask

from config import config
from extensions import db, migrate


def create_app(config_name):
    app = Flask(__name__)
    # isort 是为了把文件按好的顺序整理一下
    # black 为了检查和校验语法规格
    # pre-commit如果前两步骤没有做或者通过不允许提交
    app.config.from_object(config_name)

    db.init_app(app)
    migrate.init_app(app, db)
    return app
