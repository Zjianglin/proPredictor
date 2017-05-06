from flask import current_app
from pickle import loads, dumps
from uuid import uuid4
from threading import Thread
from . import redis
import signal
import sys
def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)


class DelayedResult(object):
    def __init__(self, key):
        self.key = key
        self._rv = None

    @property
    def return_value(self):
        if self._rv is None:
            rv = redis.get(self.key)
            if rv is not None:
                self._rv = loads(rv)
        return self._rv


def back_task(f):
    def delay(*args, **kwargs):
        qkey = current_app.config['REDIS_QUEUE_KEY']
        key = '%s:result:%s' % (qkey, str(uuid4()))
        s = dumps((f, key, args, kwargs))
        redis.rpush(current_app.config['REDIS_QUEUE_KEY'], s)
        return DelayedResult(key)
    f.delay = delay
    return f

def queue_daemon(app, rv_ttl=500):
    print('start queue_daemon...')
    signal.signal(signal.SIGINT, signal_handler)
    while 1:
        msg = redis.blpop(app.config['REDIS_QUEUE_KEY'])
        func, key, args, kwargs = loads(msg[1])
        try:
            with current_app:
                rv = func(*args, **kwargs)
        except Exception as e:
            rv = e
        if rv is not None:
            redis.set(key, dumps(rv))
            redis.expire(key, rv_ttl)

class QueueDaemon(Thread):
    def __init__(self, app=None, rv_ttl=500):
        Thread.__init__(self, daemon=True)
        self.app = app
        self.rv_ttl = rv_ttl

        print('create QueueDaemon...')
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app

    def run(self):
        print('Start QueueDaemon')
        while 1:
            msg = redis.blpop(self.app.config['REDIS_QUEUE_KEY'])
            func, key, args, kwargs = loads(msg[1])
            try:
                print('In Daemon: ', kwargs)
                rv = func(*args, **kwargs)
            except Exception as e:
                rv = e
            if rv is not None:
                redis.set(key, dumps(rv))
                redis.expire(key, self.rv_ttl)