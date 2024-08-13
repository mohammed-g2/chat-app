import os
from gevent import monkey
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
from app import create_app
from config import basedir

load_dotenv(os.path.join(basedir, '.env'))

monkey.patch_all()

app = create_app(os.environ.get('APP_CONFIG', 'default'))
print(
    'Running at => ' 
    + os.environ.get('FLASK_RUN_HOST') + ':'
    + os.environ.get('FLASK_RUN_PORT'))


@app.shell_context_processor
def shell_context():
    return dict()


@app.context_processor
def template_context():
    return dict()


WSGIServer(
    (os.environ.get('FLASK_RUN_HOST'), int(os.environ.get('FLASK_RUN_PORT'))),
    app).serve_forever()
