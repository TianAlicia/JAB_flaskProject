from redis import StrictRedis  # Redis

from com import constrants


class RedisStore:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

        self.strict_redis: StrictRedis = None

    def init_app(self, app):
        # 配置 redis 数据库
        if "REDIS_HOST" not in app.config:
            raise Exception("需要先加载redis配置信息")
        self.strict_redis = StrictRedis(
            host=app.config["REDIS_HOST"],
            port=app.config["REDIS_PORT"],
            decode_responses=True,
        )
        # current_app.strict_redis.xxx 的方式进行调用
        setattr(app, "strict_redis", self.strict_redis)

    def store_chapter_image(self, code_id, text):
        self.strict_redis.setex(
            "ImageCode_" + code_id, constrants.IMAGE_CODE_REDIS_EXPIRES, text
        )

    def get_chapter_image(self, code_id):
        return self.strict_redis.get("ImageCode_" + code_id)

    # def store_sms_code(self, mobile, sms_code):
    #     self.strict_redis.setex(
    #         "sms_code_" + mobile, constrants.SMS_CODE_REDIS_EXPIRES, sms_code
    #     )
    #
    # def get_sms_code(self, mobile):
    #     return self.strict_redis.get("sms_code_" + mobile)
