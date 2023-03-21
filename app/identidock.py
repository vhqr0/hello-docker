import os
import hashlib
import threading
import html
import sqlite3
import logging

from flask import Flask, Response, request
import requests
import redis

LOG_FORMAT = '%(asctime)s %(name)s %(levelname)s %(message)s'
LOG_DATEFMT = '%y-%m-%d %H:%M:%S'

NAME = 'vhqr'
SALT = 'f371792d-8160-4e73-9d61-a6e3501acbf0'

CREATE_SQL = '''
create table if not exists count (
name varchar(255) primary key,
count integer not null default 0
)
'''

QUERY_SQL = '''
select count from count where name = ?
'''

UPDATE_SQL = '''
replace into count (name, count) values (?, ?)
'''

DEBUG = os.getenv('ENV') == 'DEV'

app = Flask(__name__)
logger = logging.getLogger(__name__)
logging.basicConfig(level='DEBUG' if DEBUG else 'INFO',
                    format=LOG_FORMAT,
                    datefmt=LOG_DATEFMT)
cache = redis.StrictRedis(host='redis', port=6379, db=0)

db = sqlite3.connect('/data/count.db', check_same_thread=False)
dblock = threading.Lock()

try:
    cur = db.cursor()
    cur.execute(CREATE_SQL)
except Exception as e:
    logger.error('initdb failed for %s', e)


def updatedb(name):
    count = 0
    with dblock:
        try:
            cur = db.cursor()
            cur.execute(QUERY_SQL, (name, ))
            rows = cur.fetchall()
            if len(rows) != 0:
                count = int(rows[0][0])
            count += 1
            cur.execute(UPDATE_SQL, (name, count))
            db.commit()
        except Exception as e:
            logger.error('updatedb failed for: %s', e)
    return count


@app.route('/', methods=['GET', 'POST'])
def mainpage():
    if request.method == 'POST':
        name = request.form.get('name') or NAME
    else:
        name = NAME
    name = html.escape(name)
    count = updatedb(name)
    name_hash = hashlib.sha256((SALT + name).encode()).hexdigest()
    header = '<html><head><title>Identidock</title></head><body>'
    body = '''
    <form method="POST">
    Hello <input type="text" name="name" value="{}"/>
    <input type="submit" value="submit"/>
    </form>
    <p>You look like a: <img src="/monster/{}"/></p>
    <p>You have visited: {} times</p>
    '''.format(name, name_hash, count)
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
