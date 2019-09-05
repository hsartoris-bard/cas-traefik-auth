from os import path, getcwd
import flask
from flask import Flask, render_template, session, redirect, send_from_directory, Response
from werkzeug.middleware.dispatcher import DispatcherMiddleware
#from sassutils.wsgi import SassMiddleware

from flask_cas import CAS, login, logout, login_required

import logging

app = Flask(__name__)
#app.wsgi_app = SassMiddleware(app.wsgi_app,
#        { 'app': ('static/sass', 'static/css', '/static/css') }
#        )
#cas = CAS(app, '/cas')
cas = CAS(app)
app.secret_key = "Nie2thahRe1je3eipee4"
app.config['CAS_SERVER'] = "https://cas.k8s.bard.edu"
app.config['APPLICATION_ROOT'] = "/proxy"
app.debug = True
#app.config['CAS_AFTER_LOGIN'] = "secure"

@app.route("/")
def main():
    return render_template("index.html")

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

#@app.route("/auth")
#def auth():
#    #return Response("{'a':'b'}", status=201, mimetype='application/json')
#    return "", 200

@app.route("/bip")
def bip():
    return render_template("bip.html")

@app.route("/bip/login")
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

@app.route("/auth/<service>")
def auth_path(service):
    debug = flask.current_app.logger.debug
    print("CAS info:")
    print(dir(cas))
    #print(f"CAS username is None: {cas.username is None}")
    #if 'CAS_USERNAME' not in flask.session:
    if cas.username is None:
        debug("No CAS username detected; will redirect to login")
        env = flask.request.environ
        #flask.session['TRAEFIK_HOST'] = "https://redis.k8s.bard.edu/"
        flask.session['CAS_AFTER_LOGIN_SESSION_URL'] = "https://redis.k8s.bard.edu/"
        #flask.session['TRAEFIK_HOST'] = \
        #        f"{env['HTTP_X_FORWARDED_PROTO']}://{env['HTTP_X_FORWARDED_HOST']}{env['HTTP_X_FORWARDED_URI']}"
        #debug(f"Storing return-to host as {flask.session['TRAEFIK_HOST']}")

        return redirect(flask.url_for('cas.login', 
            service=service,
            _external=True))
    #print(f"script root: {flask.request.script_root}\nfull_path:{flask.request.full_path}")
    #print(f"{cas.username:}")
    #return redirect("/login")

    #if 'TRAEFIK_HOST' in flask.session:
    #    redir = flask.session.pop('TRAEFIK_HOST')
    #    debug(f"Redirecting to {redir}")
    #    del flask.session['TRAEFIK_HOST']
    #    return redirect(redir, 302)

    response = Response("OK", 200)
    response.headers['X-Auth-User'] = cas.username
    return response

@app.route("/test")
def test_auth():
    print("got here")
    return "OK", 200

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(path.join(getcwd(), 'static'), filename)

def simple_wsgi(env, resp):
    resp(b'200 OK', [(b'Content-Type', b'text/plain')])
    return [b'Hello WSGI']

app.wsgi_app = DispatcherMiddleware(simple_wsgi, {"/proxy": app.wsgi_app})

if __name__ == "__main__":
    app.config['SESSION_TYPE'] = "filesystem"
    app.config['SERVER_NAME'] = "galactica:5000"
    app.debug = True
    app.run()
