"""
Lists edits awaiting moderation.
"""

__author__ = 'harihar'

import flask
from geo.core.moderation import Moderation
from geo.core.main import Main

db = None
mod = flask.Blueprint("moderation", __name__)


@mod.route("/moderation/")
def view():

    main = Main(db)
    moderation = Moderation(db)

    return flask.render_template("moderation.html")
