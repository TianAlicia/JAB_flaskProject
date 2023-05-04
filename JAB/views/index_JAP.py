from flask import Blueprint, current_app, render_template

index_JAP = Blueprint("index", __name__)


@index_JAP.route("/")
def hello_world():
    return render_template("JAB/index.html")


@index_JAP.route("/logo-social.ico")
def favicon():
    return current_app.send_static_file("logo-social.ico")
