__author__ = 'harihar'

import flask


mod = flask.Blueprint("partners", __name__)

@mod.route("/partners")
def view():

    return flask.render_template("partners.html")
