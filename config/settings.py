class BaseConfig():
   API_PREFIX = '/api'
   TESTING = False
   DEBUG = False
   SECRET_KEY = '@!s3cr3t'
   AGENT_SOCK = 'cmdsrv__0'

class DevConfig(BaseConfig):
   FLASK_ENV = 'development'
   DEBUG = True
   CELERY_BROKER = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   REDIS_URL = "redis://localhost:6379/0"
   IFACE = "eno2"

class ProductionConfig(BaseConfig):
   FLASK_ENV = 'production'
   CELERY_BROKER = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   REDIS_URL = "redis://localhost:6379/0"

class TestConfig(BaseConfig):
   FLASK_ENV = 'development'
   TESTING = True
   DEBUG = True
   # make celery execute tasks synchronously in the same process
   CELERY_ALWAYS_EAGER = True
