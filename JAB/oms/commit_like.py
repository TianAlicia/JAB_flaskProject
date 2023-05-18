from datetime import datetime

from extensions import db


class CommentLikeORM(db.Model):
    __tablename__ = "bbs_comment_like"

    user_id = db.Column(
        "user_id", db.Integer, db.ForeignKey("bbs_user.id"), primary_key=True
    )
    comment_id = db.Column(
        "comment_id", db.Integer, db.ForeignKey("bbs_comment.id"), primary_key=True
    )

    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
