from datetime import datetime

from extensions import db


class ArticleORM(db.Model):
    """新闻"""

    __tablename__ = "bbs_article"

    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(64), nullable=False)
    author_pfp = db.Column(db.String(256))
    title = db.Column(db.String(256), nullable=False)
    source = db.Column(db.String(64), nullable=False)
    digest = db.Column(db.String(512), nullable=False)
    content = db.Column(db.Text, nullable=False)
    clicks = db.Column(db.Integer, default=0)
    index_image_url = db.Column(db.String(256))
    status = db.Column(db.Integer, default=0)
    reason = db.Column(db.String(256))

    category_id = db.Column(db.Integer, db.ForeignKey("bbs_category.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("bbs_user.id"))

    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    comment_list = db.relationship("CommentORM", lazy="dynamic")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_to_db(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, author=None, author_pfp=None, title=None, content=None, index_image_url=None, category_id=None, update_time=None):
        if author:
            self.author = author
        if author_pfp:
            self.author_pfp = author_pfp
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
