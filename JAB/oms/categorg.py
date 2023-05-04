from datetime import datetime

from extensions import db


class CategoryORM(db.Model):
    """新闻分类"""

    __tablename__ = "bbs_category"

    id = db.Column(db.Integer, primary_key=True)  # 分类编号
    name = db.Column(db.String(64), nullable=False)  # 分类名

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )  # 记录的更新时间

    article_list = db.relationship("ArticleORM", backref="category", lazy="dynamic")
