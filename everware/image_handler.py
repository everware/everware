from tornado import gen
from tornado.locks import Event
from tornado.ioloop import IOLoop
from itertools import count


def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class ImageHandler():

    def __init__(self):
        self._images = {}

    def get_waiter(self, image_name):
        if image_name not in self._images:
            self._images[image_name] = ImageMutex()
        return self._images[image_name]


class ImageMutex():

    def __init__(self):
        self._mutex = Event()
        self._blocked = count()
        self._building_log = []
        self._exception = None

    @gen.coroutine
    def block(self):
        value = self._blocked.__next__()  # single bytecode operation
        if value:
            yield self._mutex.wait()
        return value

    def __enter__(self):
        if self._exception is not None:
            raise self._exception
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._building_log = []
        if isinstance(exc_value, Exception):
            self._exception = exc_value
        self._mutex.set()

    def add_to_log(self, message, level=1):
        self._building_log.append({
            'text': message,
            'level': level
        })

    @property
    def building_log(self):
        return self._building_log

    @property
    def last_exception(self):
        return self._exception
