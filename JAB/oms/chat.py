from datetime import datetime

from extensions import db
import json


class ChatORM(db.Model):

    __tablename__ = "bbs_chat"

    user1 = db.Column(db.Integer, primary_key=True)
    user2 = db.Column(db.Integer, primary_key=True)
    conversa = db.Column(db.JSON)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_to_db(self):
        db.session.delete(self)
        db.session.commit()

    def update(self, conversa=None):
        self.conversa = json.dumps(conversa)
        db.session.commit()
