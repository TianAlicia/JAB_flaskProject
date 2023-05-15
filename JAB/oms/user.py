from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

"""user_follows tambien esta en user.py"""

tb_user_follows = db.Table(
    "bbs_user_fans",
    db.Column(
        "follower_id", db.Integer, db.ForeignKey("bbs_user.id"), primary_key=True
    ),  # 粉丝id
    db.Column(
        "followed_id", db.Integer, db.ForeignKey("bbs_user.id"), primary_key=True
    ),  # 被关注人的id
)


class UserORM(db.Model, UserMixin):
    """用户"""

    __tablename__ = "bbs_user"

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )  # 记录的更新时间

    id = db.Column(db.Integer, primary_key=True)  # 用户编号
    nick_name = db.Column(db.String(32), unique=True, nullable=False)  # 用户昵称
    password_hash = db.Column(db.String(128), nullable=False)  # 加密的密码
    mobile = db.Column(db.String(11), unique=True, nullable=False)  # 手机号
    email = db.Column(db.String(50))  # 游戏地址
    avatar_url = db.Column(db.String(256), default='/static/images/worm.jpg')  # 用户头像路径
    last_login = db.Column(db.DateTime, default=datetime.now)  # 最后一次登录时间
    is_admin = db.Column(db.Boolean, default=False)
    signature = db.Column(db.String(512))  # 用户签名

    gender = db.Column(db.Enum("Home", "Dona"), default="Home")  # 男  # 女


    # 当前用户所发布的新闻
    article_list = db.relationship("ArticleORM", backref="user", lazy="dynamic")

    # 当前用户收藏的所有新闻
    collection_article_list = db.relationship(
        "ArticleORM", secondary="bbs_user_collection", lazy="dynamic"
    )  # 用户收藏的新闻
    # dynamic如果不调用属性, 就不会进行动态查询

    # 用户所有的粉丝，添加了反向引用 followed ，代表用户都关注了哪些人
    followers = db.relationship(
        "UserORM",
        secondary=tb_user_follows,
        primaryjoin=id == tb_user_follows.c.followed_id,
        secondaryjoin=id == tb_user_follows.c.follower_id,
        backref=db.backref("followed", lazy="dynamic"),
        lazy="dynamic",
    )

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
