from datetime import datetime
from flask_babel import gettext
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db

tb_user_follows = db.Table(
    "bbs_user_fans",
    db.Column(
        "follower_id", db.Integer, db.ForeignKey("bbs_user.id"), primary_key=True
    ),
    db.Column(
        "followed_id", db.Integer, db.ForeignKey("bbs_user.id"), primary_key=True
    ),
)


class UserORM(db.Model, UserMixin):
    __tablename__ = "bbs_user"

    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    id = db.Column(db.Integer, primary_key=True)
    nick_name = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    mobile = db.Column(db.String(11), unique=True, nullable=False)
    email = db.Column(db.String(50))
    avatar_url = db.Column(db.String(256))
    last_login = db.Column(db.DateTime, default=datetime.now)
    is_admin = db.Column(db.Boolean, default=False)
    signature = db.Column(db.String(512))

    gender = db.Column(db.Enum("Home","Dona"), default="Home")

    article_list = db.relationship("ArticleORM", backref="user", lazy="dynamic")
    comment_list = db.relationship("CommentORM", backref="user", lazy="dynamic")

    collection_article_list = db.relationship(
        "ArticleORM", secondary="bbs_user_collection", lazy="dynamic"
    )

    comment_like_list = db.relationship(
        "CommentORM", secondary="bbs_comment_like", lazy="dynamic"
    )

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
        raise AttributeError(gettext("Contrasenya errònia"))

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()
