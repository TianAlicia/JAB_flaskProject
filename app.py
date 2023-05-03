from config import config
from flask import Flask

app = Flask(__name__)
# isort 是为了把文件按好的顺序整理一下
# black 为了检查和校验语法规格
# pre-commit如果前两步骤没有做或者通过不允许提交
app.config.from_object(config["dev"])


@app.route("/")
def hello():
    return "hello world"


if __name__ == "__main__":
    app.run()
