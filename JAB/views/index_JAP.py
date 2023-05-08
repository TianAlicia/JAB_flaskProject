import re
from random import randint

from flask import (
    Blueprint,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
)
from flask_login import login_user, logout_user

from com.gen_captcha import get_captcha_image

# from com.sms import send_sms
from extensions import redis_store
from JAB.oms import ArticleORM, CategoryORM, UserORM

index_JAP = Blueprint("index", __name__)


@index_JAP.route("/")
def hello_world():
    return render_template("JAB/index.html")


@index_JAP.route("/logo-social.ico")
def favicon():
    return current_app.send_static_file("logo-social.ico")


@index_JAP.route("/login", methods=["POST", "GET"])
def login_view():
    if request.method == "GET":
        return render_template("JAB/login.html")
    # data = request.get_json()
    # Email = data.get("Email")
    # mobile = data.get("mobile")
    username = request.json.get("username")
    password = request.json.get("password")

    captcha_code = request.json.get("captcha_code")
    captcha_code_uuid = request.json.get("captcha_code_uuid")
    # 校验参数
    captcha_code2 = redis_store.get_chapter_image(captcha_code_uuid)
    if not captcha_code or not captcha_code2:
        return {"status": "fail", "message": "验证码错误"}

    if captcha_code != captcha_code2:
        return {"status": "fail", "message": "验证码错误"}
    if not username or not password:
        return {"status": "fail", "message": "请填写完整信息"}

    user: UserORM = UserORM.query.filter_by(nick_name=username).first()
    if not user:
        return {"status": "fail", "message": "用户名不存在"}
    if not user.check_password(password):
        return {"status": "fail", "message": "密码错误"}
    login_user(user)
    return {"status": "success", "message": "登录成功"}


@index_JAP.route("/register", methods=["POST", "GET"])
def register_view():
    if request.method == "GET":
        return render_template("JAB/register.html")
    data = request.get_json()
    Email = data.get("Email")
    mobile = data.get("mobile")
    nickname = data.get("nom")
    password = data.get("password")
    # print(password)
    # if not Email or not nickname or not password:
    #     return {"status": "fail", "message":"pone informacion completada"}
    user: UserORM = UserORM()
    user.email = Email
    user.mobile = mobile
    user.nick_name = nickname
    user.password = password
    user.sava_to_db()
    return {"status": "sucess", "message": "registre correcto"}


@index_JAP.route("/get_captcha")
def get_captcha_view():
    uuid = request.args.get("image_code_uuid")
    img, text = get_captcha_image()
    # 将文字保存到 redis
    # print(img, text)
    redis_store.store_chapter_image(uuid, text)
    # 图片返回给浏览器
    resp = make_response(img)
    resp.content_type = "image/png"
    return resp


@index_JAP.route("/sms_code", methods=["POST"])
def sms_code_view():
    captcha_code = request.json.get("captcha_code")
    captcha_code_uuid = request.json.get("captcha_code_uuid")
    Email = request.json.get("Email")
    # if not Email.find('@'):
    #     return {
    #     'status': 'sucess',
    #     'message': 'email incorrecto'
    # }

    # 检查验证码是否正确
    captcha_code2 = redis_store.get_chapter_image(captcha_code_uuid)
    if not captcha_code2:
        return {"status": "fail", "message": "验证码不存在"}
    if captcha_code != captcha_code2:
        return {"status": "fail", "message": "验证码输入错误"}
    return {"status": "sucess", "message": "envia correcto, codig:1234"}


@index_JAP.route("/logout")
def logout_view():
    logout_user()
    return redirect("/")
