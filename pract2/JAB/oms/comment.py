from datetime import datetime

from extensions import db


class CommentORM(db.Model):
    __tablename__ = "bbs_comment"

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    like_count = db.Column(db.Integer, default=0)

    user_id = db.Column(db.Integer, db.ForeignKey("bbs_user.id"), nullable=False)

    article_id = db.Column(db.Integer, db.ForeignKey("bbs_article.id"), nullable=False)

    parent_id = db.Column(db.Integer, db.ForeignKey("bbs_comment.id"))

    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    parent = db.relationship("CommentORM", remote_side=[id], backref="child")
    user_like_list = db.relationship(
        "UserORM",
        secondary="bbs_comment_like",
        lazy="dynamic",
    )
