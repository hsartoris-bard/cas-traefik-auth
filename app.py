from os import path, getcwd
import flask
from flask import Flask, render_template, session, redirect, send_from_directory, Response
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from flask_cas import CAS, login, logout, login_required

import logging

app = Flask(__name__)
cas = CAS(app)
app.secret_key = "Nie2thahRe1je3eipee4"
app.config['CAS_SERVER'] = "https://login.bard.edu"
app.config['APPLICATION_ROOT'] = "/bip"
app.debug = True
app.config['CAS_AFTER_LOGIN'] = "auth"

@app.route("/secure")
@login_required
def secure():
    uid = cas.username
    logging.info(f"CAS object: {cas}")
    #attributes = cas.attributes
    logging.info(f"CAS username {uid}")
    #if attributes: logging.info(f"CAS attributes {attributes}")
    return render_template("secure.html", cas=cas)

@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")

@app.route("/")
def bip():
    return render_template("bip.html")

@app.route("/auth")
@login_required
def bip_login():
    edauser = 'student'
    edapass = 'rh5'
    url_base = "https://bip.bard.edu/cgi-bin/ibi_cgi/ibiweb.exe"
    params = [
            f"IBIC_user={edauser}",
            f"FUSER={cas.username}",
            f"IBIC_pass={edapass}",
            "IBIWF_action=WF_SIGNON",
            "WF_SIGNON_MESSAGE=https://bip.bard.edu/mainmenu.html"
            ]
    return redirect(f"{url_base}?{'&'.join(params)")

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(path.join(getcwd(), 'static'), filename)

def simple_wsgi(env, resp):
    resp(b'200 OK', [(b'Content-Type', b'text/plain')])
    return [b'Hello WSGI']

app.wsgi_app = DispatcherMiddleware(simple_wsgi, {"/bip": app.wsgi_app})

if __name__ == "__main__":
    app.config['SESSION_TYPE'] = "filesystem"
    app.config['SERVER_NAME'] = "galactica:5000"
    app.debug = True
    app.run()
