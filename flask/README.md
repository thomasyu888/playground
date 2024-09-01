# Flask exploration

This is to explore hosting of APIs using Flask, but more importantly, it is to explore the use fo Celery for the asynchronous repsonse-reply design pattern for APIs that require long processing jobs.

## Asyncronous response-reply design pattern

Following this article: https://blog.miguelgrinberg.com/post/using-celery-with-flask.

1. Follow instructions here: https://flask.palletsprojects.com/en/3.0.x/installation/
1. https://docs.celeryq.dev/en/stable/getting-started/first-steps-with-celery.html
1. In two separate windows

    ```
    celery -A app.celery worker --loglevel=info
    ```

    ```
    flask run
    ```

1. See example outputs

    ```
    curl -X POST http://localhost:5000/validateManifest \
     -H "Content-Type: application/json" \
     -d '{"key1": "value1", "key2": "value2"}'
    # {"task_id":"80777733-76f2-44af-a11c-f01a154eb56e"}
    ```

    ```
    curl http://localhost:5000/status/80777733-76f2-44af-a11c-f01a154eb56e
    # {"current":13,"state":"PROGRESS","status":"Loading harmonic orbiter...","total":31}
    curl http://localhost:5000/status/80777733-76f2-44af-a11c-f01a154eb56e
    # {"current":100,"result":42,"state":"SUCCESS","status":"Task completed!","total":100}
    ```
