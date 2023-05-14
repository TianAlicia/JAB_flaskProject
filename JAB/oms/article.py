from datetime import datetime

from extensions import db


class ArticleORM(db.Model):
    """新闻"""

    __tablename__ = "bbs_article"

    id = db.Column(db.Integer, primary_key=True)  # 新闻编号
    title = db.Column(db.String(256), nullable=False)  # 新闻标题
    source = db.Column(db.String(64), default="")  # 新闻来源
    digest = db.Column(db.String(512), default="")  # 新闻摘要
    content = db.Column(db.Text, nullable=False)  # 新闻内容
    clicks = db.Column(db.Integer, default=0)  # 浏览量
    index_image_url = db.Column(db.String(256))  # 新闻列表图片路径
    status = db.Column(db.Integer, default=0)  # 当前新闻状态 如果为0代表审核通过，1代表审核中，-1代表审核不通过
    reason = db.Column(db.String(256))  # 未通过原因，status = -1 的时候使用

    category_id = db.Column(db.Integer, db.ForeignKey("bbs_category.id"))  # 分类的 id

    user_id = db.Column(db.Integer, db.ForeignKey("bbs_user.id"))

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(
        db.DateTime, default=datetime.now, onupdate=datetime.now
    )  # 记录的更新时间

    # 当前新闻的所有评论
    comment_list = db.relationship("CommentORM", lazy="dynamic")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_to_db(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, title=None, content=None, index_image_url=None, category_id=None, update_time=None):
        if title:
            self.title = title
        if content:
            self.content = content
        if index_image_url:
            self.index_image_url = index_image_url
        if category_id:
            self.category_id = category_id
        if update_time:
            self.update_time = update_time

        db.session.commit()
