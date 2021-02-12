from app.config import Config
from celery import Celery


config = Config().get_config()
backend_url = config.get("TaskQueue", "backend_url")
broker_url = config.get("TaskQueue", "broker_url")

app = Celery('tasks', backend=backend_url, broker=broker_url, include=['app.queue.tasks'])

if __name__ == '__main__':
    app.start()
