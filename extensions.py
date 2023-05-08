from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# from JAB import register_blueprint
from com.redis_utils import RedisStore

db = SQLAlchemy()
migrate = Migrate(db)
redis_store = RedisStore()


def register_plugin(app):
    db.init_app(app)
    migrate.init_app(app, db)
    redis_store.init_app(app)
