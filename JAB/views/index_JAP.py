from flask import Blueprint, render_template

index_JAP = Blueprint("index", __name__)


@index_JAP.route("/")
def hello_world():
    return render_template("JAB/index.html")
