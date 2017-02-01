"""
Saves moderation decision.
"""

__author__ = 'harihar'

import flask
import time


db = None
mod = flask.Blueprint("moderation_submit", __name__)


@mod.route("/moderationsubmit/")
def view():

    session = flask.session

    if not session.get("moderator_user", False):
        flask.abort(403)
        return

    moderation = flask.request.args.get("moderation", None)
    comment = flask.request.args.get("moderation_comment", "")
    description_id = flask.request.args.get("geoid", "")
    if not moderation in ["1", "0"] or not description_id:
        flask.abort(403)
        return

    data = {
        "moderated": 1,
        "moderator_id": session.get("user_id"),
        "accepted": moderation,
        "comments": comment,
        "description_id": description_id,
        "moderated_time": time.gmtime()
    }
    sql = "UPDATE History SET \
`Moderated`=%(moderated)s, \
`Moderator_ID`=%(moderator_id)s, \
`Accepted`=%(accepted)s, \
`Comments`=%(comments)s, \
`Moderated_Time_Stamp`=%(moderated_time)s \
WHERE `Description_ID`=%(description_id)s"

    db_conn = db.session
    session = db_conn.cursor(dictionary=True)

    session.execute(sql, data)
    db_conn.commit()

    flask.flash("The moderation was successful.")
    return flask.redirect(flask.url_for('form.factsheet', description_id=description_id))