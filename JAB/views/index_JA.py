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
from qingdeng.orms import ArticleORM, CategoryORM, UserORM

from com.gen_captcha import get_captcha_image
from com.sms import send_sms
from extensions import redis_store

index_JAP = Blueprint("index", __name__)


@index_bp.route("/")
def hello_world():
    # 显示分类数据
    cate_list = CategoryORM.query.all()

    # 第几页 每一页多少条数据 是什么分类
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    cid = request.args.get("cid", default=1, type=int)

    filters = []
    if cid != 1:  # 如果不是 1 就查询指定分类
        filters.append(ArticleORM.category_id == cid)  # 分组分类的 id

    # 展示文章数据
    paginate = (
        ArticleORM.query.order_by(ArticleORM.create_time.desc())
        .filter(*filters)
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    hot_article_list = (
        ArticleORM.query.order_by(ArticleORM.clicks.desc()).limit(10).all()
    )

    # 2中显示方式: 1. 先获取数据,然后传递到模板进行渲染 2. 可以将分页对象直接传递到模板对象
    return render_template(
        "bbs/index.html",
        cate_list=cate_list,
        paginate=paginate,
        hot_article_list=hot_article_list,
    )


@index_bp.route("/favicon.ico")
def favicon():
    return current_app.send_static_file("favicon.ico")


@index_bp.route("/login", methods=["GET", "POST"])
def login_view():
    if request.method == "GET":
        return render_template("bbs/login.html")

    mobile = request.json.get("mobile")
    password = request.json.get("password")
    captcha_code = request.json.get("captcha_code")
    captcha_code_uuid = request.json.get("captcha_code_uuid")

    # 校验参数
    captcha_code2 = redis_store.get_chapter_image(captcha_code_uuid)
    if not captcha_code or not captcha_code2:
        return {"status": "fail", "message": "验证码错误"}

    if captcha_code != captcha_code2:
        return {"status": "fail", "message": "验证码错误"}
    if not mobile or not password:
        return {"status": "fail", "message": "请填写完整信息"}

    user: UserORM = UserORM.query.filter_by(mobile=mobile).first()
    if not user:
        return {"status": "fail", "message": "用户名不存在"}
    if not user.check_password(password):
        return {"status": "fail", "message": "密码错误"}
    login_user(user)
    return {
        "status": "success",
        "message": "登录成功",
        "next": request.json.get("next", None),
    }


@index_bp.route("/register", methods=["POST", "GET"])
def register_view():
    if request.method == "GET":
        return render_template("bbs/register.html")
    mobile = request.json.get("mobile")
    mobile_code = request.json.get("mobile_code")
    mobile_code2 = redis_store.get_sms_code(mobile)
    # print(mobile, mobile_code, mobile_code2)
    if not mobile or not mobile_code:
        return {"status": "fail", "message": "请填写完整信息"}
    if not mobile_code2:
        return {"status": "fail", "message": "验证码不存在"}
    if mobile_code2 != mobile_code:
        return {"status": "fail", "message": "手机号不正确"}

    nickname = request.json.get("nickname")
    password = request.json.get("password")
    user: UserORM = UserORM()
    user.mobile = mobile
    user.password = password
    user.nick_name = nickname
    user.save_to_db()
    return {"status": "success", "message": "注册成功"}


@index_bp.route("/get_captcha")
def get_captcha_view():
    uuid = request.args.get("image_code_uuid")
    img, text = get_captcha_image()
    # 将文字保存到 redis
    redis_store.store_chapter_image(uuid, text)
    # 图片返回给浏览器
    resp = make_response(img)
    resp.content_type = "image/png"
    return resp


@index_bp.route("/sms_code", methods=["POST"])
def sms_code_view():
    captcha_code = request.json.get("captcha_code")
    captcha_code_uuid = request.json.get("captcha_code_uuid")
    mobile = request.json.get("mobile")
    if not re.match(r"^1\d{10}$", mobile):
        return {"status": "fail", "message": "手机号不符合格式"}
    # 检查验证码是否正确
    captcha_code2 = redis_store.get_chapter_image(captcha_code_uuid)
    if not captcha_code2:
        return {"status": "fail", "message": "验证码不存在"}
    if captcha_code != captcha_code2:
        return {"status": "fail", "message": "验证码输入错误"}
    # 发送短信
    # 3. 发送短信
    # 3.1 生成短信验证码
    sms_code = randint(0, 999999)
    sms_code = "%06d" % sms_code

    # 3.2 发送短信
    # send_sms(mobile, sms_code)
    current_app.logger.info(f"sms_code:{sms_code}")
    redis_store.store_sms_code(mobile, sms_code)
    # 记录用户的短信验证码

    return {"status": "success", "message": "发送短信成功,请在60s之内输入"}


@index_bp.route("/logout")
def logout_view():
    logout_user()
    return redirect("/")
