from flask import Flask, render_template, url_for, request, session, flash, redirect, send_file, send_from_directory, Response, jsonify
import os, sys

# add the app to the path
path = os.path.dirname(os.path.abspath(__file__))
path = path.split(os.sep)
del path[-1]
path += ['app']
directory = os.path.normpath(os.sep.join(path))
if directory not in sys.path:
    sys.path += [directory]

# import database connection
from orm import *

BASE_DIR = os.path.join('view')
STATIC_DIR = os.path.join('view','static')
app = Flask(__name__,
            template_folder=BASE_DIR,
            static_folder=STATIC_DIR)

################################ Login ################################

app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('index.html')


def start(port=80):
    app.run(host='0.0.0.0', port=port, threaded=True)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-d':
            # run in debug mode
            app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
    else:
        start()