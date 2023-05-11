import re
from random import randint
from datetime import datetime
from extensions import db

from flask import (
    Blueprint,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
    url_for,
    
)
from flask_login import login_user, logout_user
from flask_babel import Babel, gettext

from extensions import redis_store
from JAB.oms import ArticleORM, CategoryORM, UserORM
from com.gen_captcha import get_captcha_image

index_JAP = Blueprint("index", __name__)

# LANGUAGES = {
#     'cat': 'Català',
#     'es': 'Español',
#     'en': 'English'
# }

# babel = Babel()

# @babel.localeselector
# def get_locale():
#     return request.accept_languages.best_match(LANGUAGES.keys())

# babel.init_app(index_JAP)

def get_post(post_id):
    post = ArticleORM.query.filter_by(id=post_id).first()
    if not post:
        return None
    return post

@index_JAP.route("/")
def hello_world():
    posts = ArticleORM.query.all()
    return render_template("JAB/index.html", posts=posts)

@index_JAP.route("/logo-social.ico")
def favicon():
    return current_app.send_static_file("logo-social.ico")

@index_JAP.route("/login", methods=["POST", "GET"])
def login_view():
    if request.method == "GET":
        return render_template("JAB/login.html")

    username = request.json.get("username")
    password = request.json.get("password")

    captcha_code = request.json.get("captcha_code")
    captcha_code_uuid = request.json.get("captcha_code_uuid")
    # Check parameters
    captcha_code2 = redis_store.get_chapter_image(captcha_code_uuid)
    if not captcha_code or not captcha_code2:
        return {"status": "fail", "message": gettext("Invalid captcha code.")}

    if captcha_code != captcha_code2:
        return {"status": "fail", "message": gettext("Invalid captcha code.")}
    if not username or not password:
        return {"status": "fail", "message": gettext("Please enter all required fields.")}

    user = UserORM.query.filter_by(nick_name=username).first()
    if not user:
        return {"status": "fail", "message": gettext("Username does not exist.")}
    if not user.check_password(password):
        return {"status": "fail", "message": gettext("Password incorrect.")}
    login_user(user)
    return {"status": "success", "message": gettext("Login successfully.")}


@index_JAP.route("/register", methods=["POST", "GET"])
def register_view():
    if request.method == "GET":
        return render_template("JAB/register.html")

    data = request.get_json()
    Email = data.get("Email")
    mobile = data.get("mobile")
    nickname = data.get("nom")
    password = data.get("password")
    if not Email or not nickname or not password:
        return {"status": "fail", "message": gettext("Please enter all required fields.")}
    user = UserORM()
    user.email = Email
    user.mobile = mobile
    user.nick_name = nickname
    user.password = password
    user.save_to_db()
    return {"status": "success", "message": gettext("Registered successfully.")}


@index_JAP.route("/get_captcha")
def get_captcha_view():
    uuid = request.args.get("image_code_uuid")
    img, text = get_captcha_image()
    # Save text to redis
    redis_store.store_chapter_image(uuid, text)
    # Return the image to the browser
    resp = make_response


index_JAP = Blueprint("index", __name__)

# babel = Babel()

# # pybabel extract -F babel.cfg -o messages.pot --input-dirs=.
# # pybabel init -i messages.pot -d translations -l en
# # pybabel compile -d translations

# LANGUAGES = {
# 	'cat' : 'Català',
# 	'es'  : 'Español',
# 	'en'  : 'English'
# }

# def get_locale():
#     return request.accept_languages.best_match(LANGUAGES.keys())

# babel.init_app(index_JAP, locale_selector=get_locale)

def get_post(post_id):
    """
    Retrieve a post from the database given its ID.
    """
    post: ArticleORM = ArticleORM.query.filter_by(id=post_id).first()
    if not post:
        return None
    return post

@index_JAP.route("/")
def hello_world():
    posts = ArticleORM.query.all()
    return render_template("JAB/index.html", posts=posts)

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
        return {"status": "fail", "message": "Codigo vertical mal"}

    if captcha_code != captcha_code2:
        return {"status": "fail", "message": "Codigo vertical mal"}
    if not username or not password:
        return {"status": "fail", "message": "informacion completa"}

    user: UserORM = UserORM.query.filter_by(nick_name=username).first()
    if not user:
        return {"status": "fail", "message": "Usuario no exiteix"}
    if not user.check_password(password):
        return {"status": "fail", "message": "Contrasenya mal"}
    login_user(user)
    return {"status": "success", "message": "log in!!!!!"}


@index_JAP.route("/register", methods=["POST", "GET"])
def register_view():
    if request.method == "GET":
        return render_template("JAB/register.html")
    data = request.get_json()
    Email = str(data.get("Email"))

    # if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', Email):
    #     return {"status": "fail", "message": "pone email correcto"}

    mobile = data.get("mobile")
    # if not re.match(r'^6\d{8}$', mobile):
    #     return {"status": "fail", "message": "pone telefono correcto"}

    # if not re.match( r'^6\d{8}$', int(mobile)):
    #     return {"status": "fail", "message":"pone telefono correcto"}

    nickname = data.get("nom")

    password = data.get("password")
    # print(password)
    if not Email or not nickname or not password:
        return {"status": "fail", "message": "pone informacion completada"}
    user: UserORM = UserORM()
    user.email = Email
    user.mobile = mobile
    user.nick_name = nickname
    user.password = password
    user.sava_to_db()
    return {"status": "success", "message": "registre correcto"}


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
        return {"status": "fail", "message": "Codigo no exiteix"}
    if captcha_code != captcha_code2:
        return {"status": "fail", "message": "Codigo mal"}
    return {"status": "sucess", "message": "envia correcto, codig:1234"}


@index_JAP.route("/logout")
def logout_view():
    logout_user()
    return redirect('/')

@index_JAP.route('/profile')
def profile():
    return render_template("JAB/profile.html")

@index_JAP.route('/404')
def f404():
    return render_template("JAB/404.html")

@index_JAP.route("/chat")
def xat():
    return render_template("JAB/chat.html")

@index_JAP.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_url = request.form['image_url']
        category_id = request.form['category_id']

        if title:
            now = datetime.now()
            
            post: ArticleORM = ArticleORM()
            post.title = title
            post.content = content
            post.index_image_url = image_url
            post.user_id = 1
            post.category_id = category_id
            post.create_time = now
            post.update_time = now

            post.save_to_db()

            return redirect('/')
    
    return render_template("JAB/create.html")

@index_JAP.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    return render_template("JAB/post.html", post=post)

@index_JAP.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):

    post = get_post(id)
    
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image_url = request.form['index_image_url']
        category_id = request.form['category_id']

        if post:
            now = datetime.now()

            post.update(title=title, content = content, index_image_url = image_url, category_id = category_id, update_time = now)

            return redirect('/')
    
    return render_template("JAB/edit.html", post=post)


@index_JAP.route('/<int:id>/delete', methods=('POST',))
def delete(id):
    post = get_post(id)
    if post:
        post.delete_to_db()

    return redirect('/')
