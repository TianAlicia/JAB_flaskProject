from datetime import datetime

from extensions import db


class ArticleORM(db.Model):
    """新闻"""

    __tablename__ = "bbs_article"

    id = db.Column(db.Integer, primary_key=True)
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
