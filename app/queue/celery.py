from app.config import Config
from celery import Celery


config = Config().get_config()
broker_url = config.get("TaskQueue", "broker_url")

app = Celery('tasks', broker=broker_url, include=['app.queue.tasks'])

if __name__ == '__main__':
    app.start()
