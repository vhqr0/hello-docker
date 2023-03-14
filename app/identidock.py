import os
import hashlib
import html
import logging

from flask import Flask, Response, request
import requests
import redis

LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
LOG_DATEFMT = '%y-%m-%d %H:%M:%S'

NAME = 'vhqr'
SALT = 'f371792d-8160-4e73-9d61-a6e3501acbf0'

DEBUG = os.getenv('ENV') == 'DEV'

app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level='DEBUG' if DEBUG else 'INFO',
                    format=LOG_FORMAT,
                    datefmt=LOG_DATEFMT)
cache = redis.StrictRedis(host='redis', port=6379, db=0)


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    if request.method == 'POST':
        name = request.form.get('name') or NAME
    else:
        name = NAME
    name = html.escape(name)
    name_hash = hashlib.sha256((SALT + name).encode()).hexdigest()
    header = '<html><head><title>Identidock</title></head><body>'
    body = '''
    <form method="POST">
    Hello <input type="text" name="name" value="{}"/>
    <input type="submit" value="submit"/>
    </form>
    <p>You look like a: <img src="/monster/{}"/></p>
    '''.format(name, name_hash)
    footer = '</body></html>'
    return header + body + footer


@app.route('/monster/<name>')
def get_identicon(name):
    name = html.escape(name)
    image = cache.get(name)
    if image is None:
        logger.debug('missing identicon for %s', name)
        r = requests.get('http://dnmonster:8080/monster/' + name + '?size=80')
        image = r.content
        cache.set(name, image)
    return Response(image, mimetype='image/png')


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0')
