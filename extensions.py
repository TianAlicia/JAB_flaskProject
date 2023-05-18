from flask_login import LoginManager
from flask_migrate import Migrate
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy

# from JAB import register_blueprint
from com.redis_utils import RedisStore

db = SQLAlchemy()
migrate = Migrate(db)
redis_store = RedisStore()
login_manger = LoginManager()


def register_plugin(app):
    from JAB.oms import UserORM

    socketio = SocketIO(app)

    @login_manger.user_loader
    def load_user(user_id):
        return UserORM.query.get(int(user_id))

    db.init_app(app)
    migrate.init_app(app, db)
    redis_store.init_app(app)
    login_manger.init_app(app)
    socketio.init_app(app)
