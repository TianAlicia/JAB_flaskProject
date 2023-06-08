from datetime import datetime

from extensions import db


class CategoryORM(db.Model):
    """新闻分类"""

    __tablename__ = "bbs_category"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)

    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    article_list = db.relationship("ArticleORM", backref="category", lazy="dynamic")
