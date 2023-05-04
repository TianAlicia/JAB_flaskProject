from datetime import datetime

from extensions import db

# 用户收藏表，建立用户与其收藏新闻多对多的关系
# tb_user_collection = db.Table(
#     "bbs_user_collection",
#     db.Column("user_id", db.Integer, db.ForeignKey("bbs_user.id"), primary_key=True),  # 新闻编号
#     db.Column("article_id", db.Integer, db.ForeignKey("bbs_article.id"), primary_key=True),  # 分类编号
#     db.Column("create_time", db.DateTime, default=datetime.now)  # 收藏创建时间
# )


class UserCollectionORM(db.Model):
    """用户收藏表"""

    __tablename__ = "bbs_user_collection"
    user_id = db.Column(db.Integer, db.ForeignKey("bbs_user.id"), primary_key=True)
    article_id = db.Column(
        db.Integer, db.ForeignKey("bbs_article.id"), primary_key=True
    )
    create_time = db.Column(db.DateTime, default=datetime.now)
