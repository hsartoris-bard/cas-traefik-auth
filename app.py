from os import path, getcwd
from flask import Flask, render_template, session, redirect, send_from_directory
from sassutils.wsgi import SassMiddleware

from flask_cas import CAS, login, logout, login_required

import logging

app = Flask(__name__)
app.wsgi_app = SassMiddleware(app.wsgi_app,
        { 'cas-traefik-auth': ('static/sass', 'static/css', '/static/css') }
        )
cas = CAS(app, '/cas')
app.config['CAS_SERVER'] = "https://cas.k8s.bard.edu"
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

@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(path.join(getcwd(), 'static'), filename)

if __name__ == "__main__":
    app.secret_key = "Nie2thahRe1je3eipee4"
    app.config['SESSION_TYPE'] = "filesystem"
    app.config['SERVER_NAME'] = "10.20.13.96:5000"
    app.debug = True
    app.run()
