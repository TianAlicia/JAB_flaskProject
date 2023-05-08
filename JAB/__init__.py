from flask import Flask

import JAB.oms
from com.utils import setup_log
from config import config
from extensions import register_plugin
from JAB.views import register_blueprint


def create_app(config_name):
    app = Flask("JAB_flakProject")
    # isort 是为了把文件按好的顺序整理一下
    # black 为了检查和校验语法规格
    # pre-commit如果前两步骤没    register_blueprint(app)有做或者通过不允许提交
    app.config.from_object(config[config_name])
    register_plugin(app)
    register_blueprint(app)

    return app


"""
数据库建模：
    需求文档---->  用户，文章，评论，分类，

"""
