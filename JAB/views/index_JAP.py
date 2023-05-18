import hashlib
import re
from datetime import datetime
from random import randint

from flask import (
    Blueprint,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
)
from flask_babel import Babel, gettext
from flask_login import current_user, login_required, login_user, logout_user

from com.gen_captcha import get_captcha_image
from extensions import db, redis_store
from JAB.oms import ArticleORM, CategoryORM, CommentORM, UserORM

# from com.cos import TenCos


index_JAP = Blueprint("index", __name__)
index_JAP.secret_key = "joanaliciabernat"


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


def get_user():
    if not current_user:
        return None

    user = UserORM.query.filter_by(
        id=current_user.id
    ).first()  # Adjust the query based on your ORM

    return user


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
        return {
            "status": "fail",
            "message": gettext("Please enter all required fields."),
        }

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
        return {
            "status": "fail",
            "message": gettext("Please enter all required fields."),
        }
    user = UserORM()
    user.email = Email
    user.mobile = mobile
    user.nick_name = nickname
    user.password = password
    user.avatar_url = "/static/images/worm.jpg"
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
    # presenta el categoria
    cate_list = CategoryORM.query.all()
    # El nombre de pàgines, quantes dades per pàgina i quina categoria
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    cid = request.args.get("cid", default=1, type=int)
    filters = []
    if cid != 1:
        filters.append(ArticleORM.category_id == cid)

    # presenta el filter de articules
    paginate = ArticleORM.query.filter(*filters).paginate(
        page=page, per_page=per_page, error_out=False
    )
    # posts = ArticleORM.query.all()
    hot_article_list = (
        ArticleORM.query.order_by(ArticleORM.clicks.desc()).limit(10).all()
    )
    return render_template(
        "JAB/index.html",
        cate_list=cate_list,
        paginate=paginate,
        hot_article_list=hot_article_list,
    )

    # return render_template("JAB/index.html", posts=posts)


@index_JAP.route("/article/<int:article_id>")
def article_view(article_id):
    article: ArticleORM = ArticleORM.query.get(article_id)
    hot_article_list = (
        ArticleORM.query.order_by(ArticleORM.clicks.desc()).limit(10).all()
    )
    #
    # # 文章是否已经被收藏过了
    is_collect = False
    user: UserORM = current_user
    if user.is_active:
        is_collect = True if (article in user.collection_article_list) else False

    author: UserORM = article.user
    comment_list = article.comment_list  # 可以对评论进行排序
    is_followed = False
    if author:  # 文章有作者才能判断用户是不是作者的粉丝
        is_followed = True if user in author.followers else False
    return render_template(
        "JAB/article.html",
        article=article,
        hot_article_list=hot_article_list,
        author=author,
        is_collect=is_collect,
        comment_list=comment_list,
        is_followed=is_followed,
    )


@index_JAP.route("/article/article_collect", methods=["POST"])
def article_collect_view():
    user: UserORM = current_user  # 已经登录的用户 匿名用户

    if not user.is_active:
        return {"status": "success", "message": "log in", "code": 4101}
    # return {"status": "success", "message": "Yes", "code": 0}

    article_id = request.json.get("article_id")
    action = request.json.get("action")
    article: ArticleORM = ArticleORM.query.get(int(article_id))
    if not article or action not in ["collect", "cancel_collect"]:
        return {"status": "success", "message": "request error", "code": 4102}
    # 前后端都需要完善
    if action == "collect":
        user.collection_article_list.append(article)
        msg = "favorito correcto"
    else:
        user.collection_article_list.remove(article)
        msg = "cancela"
    db.session.commit()
    return {"status": "success", "message": msg, "code": 0}


@index_JAP.route("/article/article_comment", methods=["POST"])
@login_required
def article_comment_view():
    article_id = request.json.get("article_id")
    content = request.json.get("comment")
    parent_id = request.json.get("parent_id")
    if not content:
        return {"status": "fail", "message": "没有评论内容"}, 401

    # 评论文章
    # 1. 拿到文章对象
    article = ArticleORM.query.get(int(article_id))
    # 2. 拿到评论对象
    comment: CommentORM = CommentORM()
    comment.user_id = current_user.id
    comment.content = content

    # 如果有父级评论
    if parent_id:
        comment.parent_id = int(parent_id)

    # 3. 评论与文字通过外键关联
    # comment.article_id = article_id
    article.comment_list.append(comment)
    db.session.add(article)
    db.session.commit()

    return {"status": "success", "message": "评论文章成功"}


"""
    评论的显示方式
    1. 返回文章的时候把评论渲染到页面(jinja2静态渲染)
    2. 返回文章之后,在前端动态请求通过前端渲染的方式实现
        2.1 实现的时候麻烦一点
        2.2 可以实现对评论的分页处理
"""


@index_JAP.route("/article/comment_like", methods=["POST"])
@login_required
def comment_like_view():
    action = request.json.get("action")
    comment_id = request.json.get("comment_id")
    # 1. 获取评论对象
    comment: CommentORM = CommentORM.query.get(int(comment_id))
    # 2. 获取点赞对象
    user: UserORM = current_user
    msg = ""
    if action == "add":
        user.comment_like_list.append(comment)
        msg = "点赞评论成功"
    elif action == "remove":
        user.comment_like_list.remove(comment)
        msg = "取消点赞评论成功"
    db.session.commit()

    return {
        "status": "success",
        "message": msg,
    }


@index_JAP.route("/article/followed_user", methods=["POST"])
@login_required
def follow_user():
    author_id = request.json.get("user_id")
    action = request.json.get("action")

    # 实现关注的逻辑
    author: UserORM = UserORM.query.get(int(author_id))
    user: UserORM = current_user
    msg = ""
    if action == "follow":
        user.followed.append(author)
        msg = "关注用户成功"
    elif action == "unfollow":
        user.followed.remove(author)
        msg = "取消关注用户成功"
    db.session.commit()
    return {"status": "success", "message": msg}


# import hashlib
#
# from flask import Blueprint, redirect, render_template, request
# from flask_login import current_user, login_required, logout_user
#
# from com.cos import TenCos
# from com.utils import upload_article_img, upload_avatar
# from qingdeng.orms import ArticleORM, CategoryORM, UserORM

# user_bp = Blueprint("user", __name__)

"""
    /个人中心
    /个人信息修改
    /我的收藏
    /我的关注
"""


@index_JAP.route("/account")
@login_required
def account_view():
    return redirect("/account/base_info")


@index_JAP.route("/account/base_info")
@login_required
def base_info_view():
    return render_template("account/base_info.html")


@index_JAP.route("/account/followed")
@login_required
def follow_view():
    # 我的关注
    user: UserORM = current_user
    followed_list = user.followed

    # 可以做分页的操作

    return render_template("account/followed.html", followed_list=followed_list)


@index_JAP.route("/account/collection")
@login_required
def account_collection_view():
    # ?page=1&per_page=10
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get("per_page", type=int, default=10)

    user: UserORM = current_user
    paginate = user.collection_article_list.paginate(
        page=page, per_page=per_page, error_out=False
    )
    return render_template("account/collection.html", paginate=paginate)


@index_JAP.route("/account/articles")
def account_articles_view():
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get("per_page", type=int, default=10)

    user: UserORM = current_user
    paginate = user.article_list.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("account/articles.html", paginate=paginate)


@index_JAP.route("/account/article_release")
def account_release_view():
    cate_list = CategoryORM.query.all()
    # 最新 是按照时间排序 不是一个类别
    cate_list.pop(0)
    return render_template("account/article_release.html", cate_list=cate_list)


@index_JAP.route("/account/info", methods=["POST"])
def account_info():
    username = request.json.get("username")
    signature = request.json.get("signature")
    gender = request.json.get("gender")
    birthday = request.json.get("birthday")

    user: UserORM = current_user
    user.nick_name = username
    user.signature = signature
    user.gender = gender
    user.create_time = birthday
    user.save_to_db()
    return {"status": "success", "message": "修改信息成功"}


@index_JAP.route("/account/password", methods=["POST"])
@login_required
def account_password():
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    user: UserORM = current_user
    if not user.check_password(old_password):
        return {"status": "fail", "message": "用户密码错误"}
    user.password = new_password
    user.save_to_db()
    logout_user()
    return {"status": "success", "message": "修改密码成功"}


# class TenCos:
# pass
#
#
# @index_JAP.route("/account/avatar", methods=["POST"])
# @login_required
# def account_avatar():
#     avatar = request.files.get("file")
#
#     filename = avatar.filename
#     # 名字相同,内容不同
#     suffix = filename.split(".")[-1]
#     # name = uuid.uuid4().hex
#     # 内容相同,名字不同 md5 摘要
#     content = avatar.stream.read()  # 读取图片之后,就没有内容了
#     name = hashlib.md5(content).hexdigest()  # 获取 md5 的值
#     # print(name)
#     filename = ".".join([name, suffix])
#     flag, avatar_url = TenCos().save_user_pic(filename=filename, file=content)
#     if flag != "ok":
#         return {"status": "success", "message": "上传头像失败"}
#     # avatar_url = upload_avatar(avatar)
#     # 图书上传成功之后头像是否有修改 ?
#     user: UserORM = current_user
#     user.avatar_url = avatar_url
#     user.save_to_db()
#     return {"status": "success", "message": "上传头像成功", "avatar_url": avatar_url}
#
#
# @index_JAP.route("/account/article_img", methods=["POST"])
# @login_required
# def account_upload_article_img():
#     avatar = request.files.get("file")
#
#     avatar_url = upload_article_img(avatar)
#     # 图书上传成功之后头像是否有修改 ?
#     user: UserORM = current_user
#     user.avatar_url = avatar_url
#     user.save_to_db()
#     return {"status": "success", "message": "上传文章图片成功", "avatar_url": avatar_url}
#
# # @index_JAP.route("/")
# # def hello_world():
# #     posts = ArticleORM.query.all()
# #     return render_template("JAB/index.html", posts=posts)


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
        return {"status": "fail", "message": "Captcha erroni"}

    if captcha_code != captcha_code2:
        return {"status": "fail", "message": "Captcha erroni"}
    if not username or not password:
        return {"status": "fail", "message": "Falten dades"}

    user: UserORM = UserORM.query.filter_by(nick_name=username).first()
    if not user:
        return {"status": "fail", "message": "Usuari no existent"}
    if not user.check_password(password):
        return {"status": "fail", "message": "Contrasenya errònia"}
    login_user(user)
    return {"status": "success", "message": "Login correcte!"}


@index_JAP.route("/register", methods=["POST", "GET"])
def register_view():
    if request.method == "GET":
        return render_template("JAB/register.html")
    data = request.get_json()
    Email = str(data.get("Email"))

    # if not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', Email):
    #     return {"status": "fail", "message": "Email invàlid"}

    mobile = data.get("mobile")
    # if not re.match(r'^6\d{8}$', mobile):
    #     return {"status": "fail", "message": "Telèfon invàlid"}

    # if not re.match( r'^6\d{8}$', int(mobile)):
    #     return {"status": "fail", "message": "Telèfon invàlid"}

    nickname = data.get("nom")

    password = data.get("password")
    # print(password)
    if not Email or not nickname or not password:
        return {"status": "fail", "message": "Falta informació"}
    user: UserORM = UserORM()
    user.email = Email
    user.mobile = mobile
    user.nick_name = nickname
    user.password = password
    user.save_to_db()
    return {"status": "success", "message": "Registre correcte"}


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
    #     return {'status': 'fail', message': 'Email incorrecte'}

    captcha_code2 = redis_store.get_chapter_image(captcha_code_uuid)
    if not captcha_code2:
        return {"status": "fail", "message": "Codi no existent"}
    if captcha_code != captcha_code2:
        return {"status": "fail", "message": "Codi erroni"}
    return {"status": "sucess", "message": "Enviament satisfactori, Codi: 1234"}


@index_JAP.route("/check_mobile")
def check_mobile():
    mobile = request.args.get("mobile")

    # Query the database for the given mobile number
    user = UserORM.query.filter_by(mobile=mobile).first()

    if user:
        return {"status": "fail", "message": "Mòvil ja existent"}
    else:
        return {"status": "success"}


@index_JAP.route("/check_name")
def check_name():
    nom = request.args.get("nom")

    # Query the database for the given name
    user = UserORM.query.filter_by(nick_name=nom).first()

    if user:
        return {"status": "fail", "message": "Nom ja existent"}
    else:
        return {"status": "success"}


@index_JAP.route("/logout")
@login_required
def logout_view():
    logout_user()
    return redirect("/")


@index_JAP.route("/profile/<author>")
def profile(author):
    user = UserORM.query.filter_by(nick_name=author).first()

    user_posts = ArticleORM.query.filter_by(author=author).all()

    return render_template("JAB/profile.html", user=user, posts=user_posts)


@index_JAP.route("/404")
def f404():
    return render_template("JAB/404.html")


@index_JAP.route("/chat")
@login_required
def xat():
    return render_template("JAB/chat.html")


@index_JAP.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        title = request.form["title"]

        if title:
            now = datetime.now()

            post: ArticleORM = ArticleORM()
            post.title = title
            post.content = request.form["content"]
            post.author = request.form["nick_name"]
            post.author_pfp = request.form["avatar_url"]
            post.index_image_url = request.form["index_image_url"]
            post.category_id = request.form["category_id"]
            post.create_time = now
            post.update_time = now

            post.save_to_db()

            return redirect("/")

    return render_template("JAB/create.html", user=get_user())


@index_JAP.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    return render_template("JAB/post.html", post=post)


@index_JAP.route("/<int:id>/edit", methods=("GET", "POST"))
@login_required
def edit(id):
    post = get_post(id)

    if request.method == "POST":
        author = request.form["nick_name"]
        author_pfp = request.form["avatar_url"]
        title = request.form["title"]
        content = request.form["content"]
        image_url = request.form["index_image_url"]
        category_id = request.form["category_id"]
        if post:
            now = datetime.now()

            post.update(
                author=author,
                author_pfp=author_pfp,
                title=title,
                content=content,
                index_image_url=image_url,
                category_id=category_id,
                update_time=now,
            )

            return redirect("/")

    return render_template("JAB/edit.html", post=post)


@index_JAP.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)
    if post:
        post.delete_to_db()

    return redirect("/")


@index_JAP.errorhandler(404)
def page_not_found(error):
    return make_response("Page not found.", 404)


@index_JAP.errorhandler(401)
def unauthorized(error):
    return make_response("Unauthorized.", 401)
