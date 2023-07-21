from config import settings


class Urls:
    # host = settings.DOMAIN
    host = "http://127.0.0.1:8080"

    _urls = {
        "main": "/",
        "news_follow": "/news/follow/",
        "news_unfollow": "/news/unfollow/"
    }

    @classmethod
    def get(cls, name):
        return cls.host + cls._urls.get(name)
