import hashlib
import re
from datetime import datetime
from random import randint

from flask import (
    Flask,
    Blueprint,
    current_app,
    make_response,
    redirect,
    render_template,
    request,
)
from flask_babel import Babel, gettext
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import func
from com.gen_captcha import get_captcha_image
from extensions import db, redis_store
from JAB.oms import ArticleORM, CategoryORM, CommentORM, UserORM
from config import config
from extensions import register_plugin
# from com.cos import TenCos

app = Flask(__name__)

def create_app(config_name):
    app.config.from_object(config[config_name])
    register_plugin(app)

    return app

babel = Babel(app)

# pybabel extract -F babel.cfg -o messages.pot --input-dirs=.
# pybabel init -i messages.pot -d translations -l en
# pybabel compile -d translations

LANGUAGES = {
    'ca': 'Català',
    'es': 'Español',
    'en': 'English'
}

def get_locale():
    return request.accept_languages.best_match(LANGUAGES.keys())

babel.init_app(app, locale_selector=get_locale)


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

@app.route("/search", methods=["POST"])
def search_view():
    if request.method == "POST":
        keyword = request.form.get("keyword")

        page = request.args.get("page", 1, type=int)  # 获取当前页数，默认为1
        per_page = 10  # 每页显示的数量

        # 查询符合关键字的文章列表，并进行分页处理
        results = ArticleORM.query.filter(
            ArticleORM.title.ilike("%{}%".format(keyword))
        ).paginate(page=page, per_page=per_page)

        return render_template(
            "JAB/search_results.html", results=results, keyword=keyword
        )

def get_post(post_id):
    """
    Retrieve a post from the database given its ID.
    """
    post: ArticleORM = ArticleORM.query.filter_by(id=post_id).first()
    if not post:
        return None
    return post


@app.route("/")
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
    return render_template('JAB/index.html', cate_list=cate_list, paginate=paginate, hot_article_list=hot_article_list)    
    # return render_template("JAB/index.html", posts=posts)


@app.route("/article/<int:article_id>")
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
    comment_list = article.comment_list
    is_followed = False
    if author:
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


@app.route("/article/article_collect", methods=["POST"])
def article_collect_view():
    user: UserORM = current_user

    if not user.is_active:
        return {"status": "success", "message": gettext("Cal fer Login"), "code": 4101}
    # return {"status": "success", "message": "Yes", "code": 0}

    article_id = request.json.get("article_id")
    action = request.json.get("action")
    article: ArticleORM = ArticleORM.query.get(int(article_id))
    if not article or action not in ["collect", "cancel_collect"]:
        return {"status": "success", "message": gettext("Error"), "code": 4102}
    # 前后端都需要完善
    if action == "collect":
        user.collection_article_list.append(article)
        msg = gettext("Favorit afegit")
    else:
        user.collection_article_list.remove(article)
        msg = gettext("Cancel·la")
    db.session.commit()
    return {"status": "success", "message": msg, "code": 0}


@app.route("/article/article_comment", methods=["POST"])
@login_required
def article_comment_view():
    article_id = request.json.get("article_id")
    content = request.json.get("comment")
    parent_id = request.json.get("parent_id")
    if not content:
        return {"status": "fail", "message": gettext("No hi ha contingut")}, 401

    article = ArticleORM.query.get(int(article_id))

    comment: CommentORM = CommentORM()
    comment.user_id = current_user.id
    comment.content = content

    if parent_id:
        comment.parent_id = int(parent_id)

    # 3. 评论与文字通过外键关联
    # comment.article_id = article_id
    article.comment_list.append(comment)
    db.session.add(article)
    db.session.commit()

    return {"status": "success", "message": gettext("Comentari correcte") }


@app.route("/article/comment_like", methods=["POST"])
@login_required
def comment_like_view():
    action = request.json.get("action")
    comment_id = request.json.get("comment_id")

    comment: CommentORM = CommentORM.query.get(int(comment_id))

    user: UserORM = current_user
    msg = ""
    if action == "add":
        user.comment_like_list.append(comment)
        msg = gettext("Comentari afegit")
    elif action == "remove":
        user.comment_like_list.remove(comment)
        msg = gettext("Comentari esborrat")

    return {
        "status": "success",
        "message": msg,
    }


@app.route("/article/followed_user", methods=["POST"])
@login_required
def follow_user():
    author_id = request.json.get("user_id")
    action = request.json.get("action")

    author: UserORM = UserORM.query.get(int(author_id))
    user: UserORM = current_user
    msg = ""
    if action == "follow":
        user.followed.append(author)
        msg = gettext("Usuari seguit")
    elif action == "unfollow":
        user.followed.remove(author)
        msg = gettext("Usuari deixat de seguir")
    db.session.commit()
    return {"status": "success", "message": msg}


@app.route("/account")
@login_required
def account_view():
    return redirect("/account/base_info")


@app.route("/account/base_info")
@login_required
def base_info_view():
    return render_template("account/base_info.html")


@app.route("/account/followed")
@login_required
def follow_view():
    user: UserORM = current_user
    followed_list = user.followed

    return render_template("account/followed.html", followed_list=followed_list)


@app.route("/account/collection")
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


@app.route("/account/articles")
def account_articles_view():
    page = request.args.get("page", type=int, default=1)
    per_page = request.args.get("per_page", type=int, default=10)

    user: UserORM = current_user
    paginate = user.article_list.paginate(page=page, per_page=per_page, error_out=False)
    return render_template("account/articles.html", paginate=paginate)


@app.route("/account/article_release")
def account_release_view():
    cate_list = CategoryORM.query.all()
    #
    # cate_list.pop(0)
    return render_template("account/article_release.html", cate_list=cate_list)


@app.route("/account/info", methods=["POST"])
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
    return {"status": "success", "message": gettext("Modificat correctament") }


@app.route("/account/password", methods=["POST"])
@login_required
def account_password():
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    user: UserORM = current_user
    if not user.check_password(old_password):
        return {"status": "fail", "message": gettext("Contrasenya incorrecte") }
    user.password = new_password
    user.save_to_db()
    logout_user()
    return {"status": "success", "message": gettext("Modificat correctament") }


@app.route("/user/posts_release", methods=["POST"])
def user_posts_release_view():
    title = request.json.get("title")
    category_id = request.json.get("category_id")
    digest = request.json.get("digest")
    image_url = request.json.get("image_url")
    content = request.json.get("content")

    article: ArticleORM = ArticleORM()
    article.title = title
    article.source = "Persina-{}".format(current_user.nick_name)
    article.user_id = current_user.id
    article.category_id = category_id
    article.digest = digest
    article.index_image_url = "static/images/user_pic.png"
    article.content = content
    article.save_to_db()
    return {"status": "success", "message": gettext("Article publicat") }


@app.route("/logo-social.ico")
def favicon():
    return current_app.send_static_file("logo-social.ico")


@app.route("/login", methods=["POST", "GET"])
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
        return {"status": "fail", "message": gettext("Captcha erroni") }

    if captcha_code != captcha_code2:
        return {"status": "fail", "message": gettext("Captcha erroni") }
    if not username or not password:
        return {"status": "fail", "message": gettext("Falten dades") }

    user: UserORM = UserORM.query.filter_by(nick_name=username).first()
    if not user:
        return {"status": "fail", "message": gettext("Usuari no existent") }
    if not user.check_password(password):
        return {"status": "fail", "message": gettext("Contrasenya errònia") }
    login_user(user)
    return {"status": "success", "message": "OK"}


@app.route("/register", methods=["POST", "GET"])
def register_view():
    if request.method == "GET":
        return render_template("JAB/register.html")
    data = request.get_json()
    Email = str(data.get("Email"))

    mobile = data.get("mobile")

    nickname = data.get("nom")

    password = data.get("password")
    # print(password)
    if not Email or not nickname or not password:
        return {"status": "fail", "message": gettext("Falta informació") }
    user: UserORM = UserORM()
    user.email = Email
    user.mobile = mobile
    user.nick_name = nickname
    user.password = password
    user.avatar_url = "static/images/user_pic.png"
    user.save_to_db()
    return {"status": "success", "message": gettext("Registre correcte") }


@app.route("/get_captcha")
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


@app.route("/sms_code", methods=["POST"])
def sms_code_view():
    captcha_code = request.json.get("captcha_code")
    captcha_code_uuid = request.json.get("captcha_code_uuid")
    Email = request.json.get("Email")

    captcha_code2 = redis_store.get_chapter_image(captcha_code_uuid)
    if not captcha_code2:
        return {"status": "fail", "message": gettext("Codi no existent") }
    if captcha_code != captcha_code2:
        return {"status": "fail", "message": gettext("Codi erroni") }
    return {"status": "sucess", "message": gettext("Enviament satisfactori, Codi: ") + 1234}


@app.route("/check_mobile")
def check_mobile():
    mobile = request.args.get("mobile")

    # Query the database for the given mobile number
    user = UserORM.query.filter_by(mobile=mobile).first()

    if user:
        return {"status": "fail", "message": gettext("Mòvil ja existent") }
    else:
        return {"status": "success"}


@app.route("/check_name")
def check_name():
    nom = request.args.get("nom")

    # Query the database for the given name
    user = UserORM.query.filter_by(nick_name=nom).first()

    if user:
        return {"status": "fail", "message": gettext("Nom ja existent") }
    else:
        return {"status": "success"}


@app.route("/logout")
@login_required
def logout_view():
    logout_user()
    return redirect("/")


@app.route("/profile/<int:user_id>")
def profile(user_id):
    user = UserORM.query.filter_by(nick_name=user_id).first()

    user_posts = ArticleORM.query.filter_by(user_id=user_id).all()

    return render_template("JAB/profile.html", user=user, posts=user_posts)


@app.route("/404")
def f404():
    return render_template("JAB/404.html")


@app.route("/chat")
@login_required
def xat():
    return render_template("JAB/chat.html")


@app.route("/create", methods=("GET", "POST"))
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


@app.route("/<int:post_id>")
def post(post_id):
    post = get_post(post_id)
    return render_template("JAB/post.html", post=post)


@app.route("/<int:id>/edit", methods=("GET", "POST"))
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


@app.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    post = get_post(id)
    if post:
        post.delete_to_db()

    return redirect("/")


@app.errorhandler(404)
def page_not_found(error):
    return make_response("Page not found.", 404)


@app.errorhandler(401)
def unauthorized(error):
    return make_response("Unauthorized.", 401)