from flask import Flask

from config import config
from extensions import db, migrate

app = Flask(__name__)
# isort 是为了把文件按好的顺序整理一下
# black 为了检查和校验语法规格
# pre-commit如果前两步骤没有做或者通过不允许提交
app.config.from_object(config["dev"])

db.init_app(app)
migrate.init_app(app, db)


@app.route("/")
def hello():
    return "hello world"


if __name__ == "__main__":
    app.run()
