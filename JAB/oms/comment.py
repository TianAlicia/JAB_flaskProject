from datetime import datetime

from extensions import db


class CommentORM(db.Model):
    """评论"""

    __tablename__ = "bbs_comment"

    id = db.Column(db.Integer, primary_key=True)  # 评论编号
    content = db.Column(db.Text, nullable=False)  # 评论内容
    like_count = db.Column(db.Integer, default=0)  # 点赞条数

    # 用户id
    user_id = db.Column(
        db.Integer, db.ForeignKey("bbs_user.id"), nullable=False
    )  # 用户id
    # 文章id
    article_id = db.Column(
        db.Integer, db.ForeignKey("bbs_article.id"), nullable=False
    )  # 新闻id

    # 评论评论 自关键的外键
    parent_id = db.Column(db.Integer, db.ForeignKey("bbs_comment.id"))  # 父评论id

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )  # 记录的更新时间

    # 父评论
    parent = db.relationship("CommentORM", remote_side=[id], backref="child")  # 自关联

    user_like_list = db.relationship(
        "UserORM",
        secondary="bbs_comment_like",
        lazy="dynamic",
    )  # 用户收藏的新闻
