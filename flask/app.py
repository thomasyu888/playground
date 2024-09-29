import random
import time

from celery import Celery
from flask import request, Flask, jsonify, url_for

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

@app.route("/")
def hello_world():
    username = request.cookies.get('username')
    print(request.cookies)
    return f"<p>Hello, World! {username} </p>"


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(30, 60)
    for i in range(total):
        # if not message or random.random() < 0.25:
        message = '{0} {1} {2}...'.format(random.choice(verb),
                                            random.choice(adjective),
                                            random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

@app.post('/validateManifest')
def validate_manifest():
    """
    curl -X POST http://localhost:5000/validateManifest \
     -H "Content-Type: application/json" \
     -d '{"key1": "value1", "key2": "value2"}'

    Returns:
        _type_: _description_
    """
    payload = request.get_json()
    task = long_task.apply_async()
    response = jsonify({'task_id': task.id})
    response.status_code = 202
    response.headers['Location'] = url_for('taskstatus', task_id=task.id)
    return response
    # return jsonify({}), 202, {'Location': url_for('taskstatus',
    #                                               task_id=task.id)}

@app.get('/status/<task_id>')
def taskstatus(task_id):
    """
    curl -X GET http://localhost:5000/status
    Returns JSONified status of the task.

    :param task_id: id of the task to query
    :type task_id: str
    :rtype: dict
    """
    task = long_task.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'state': task.state,
            'current': 0,
            'total': 1,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        # job is still running
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': task.info.get('total', 1),
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            # job finished
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 1,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)
