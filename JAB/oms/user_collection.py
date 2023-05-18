from datetime import datetime

from extensions import db


class UserCollectionORM(db.Model):
    __tablename__ = "bbs_user_collection"
    user_id = db.Column(db.Integer, db.ForeignKey("bbs_user.id"), primary_key=True)
    article_id = db.Column(
        db.Integer, db.ForeignKey("bbs_article.id"), primary_key=True
    )
    create_time = db.Column(db.DateTime, default=datetime.now)
