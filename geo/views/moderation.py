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

    moderation = Moderation(db)
    new_submits, edits = moderation.get_resources_to_moderate()

    main = Main(db)
    user_pref = main.make_html_user_pref()

    baseurl = "/geoid/"
    return flask.render_template("moderation.html",
                                 new_submits=new_submits,
                                 edits=edits,
                                 baseurl=baseurl,
                                 user_pref=user_pref)