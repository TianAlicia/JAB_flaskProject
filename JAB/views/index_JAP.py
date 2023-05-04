from flask import Blueprint

index_JAP = Blueprint("index", __name__)


@index_JAP.route("/")
def hello_world():
    return "hello!!!"
