# import os

from flask import Flask

from .index_JAP import index_JAP


def register_blueprint(app: Flask):
    # 用来注册视图的函数

    app.register_blueprint(index_JAP)
