from datetime import datetime

from extensions import db


class CommentLikeORM(db.Model):
    """评论点赞"""

    __tablename__ = "bbs_comment_like"

    user_id = db.Column(
        "user_id", db.Integer, db.ForeignKey("bbs_user.id"), primary_key=True
    )  # 用户编号
    comment_id = db.Column(
        "comment_id", db.Integer, db.ForeignKey("bbs_comment.id"), primary_key=True
    )  # 评论编号

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )  # 记录的更新时间
