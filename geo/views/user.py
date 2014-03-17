import flask
from geo.core.geo_user import GeoUser

mod = flask.Blueprint("user", __name__)


@mod.route("/login", endpoint='factsheet', methods=['POST'])
def login():

    request = flask.request
    session = flask.session

    username = request.form['username']
    password = request.form['password']

    try:
        user = GeoUser(db, username=username)
    except Exception:
        return flask.jsonify(data={'error': True})

    if user.validate_user(password):
        session['username'] = username
        session['user_fname'] = user.firstname
        session['user_lname'] = user.lastname
        session['user_id'] = user.user_id
        data = {}
        data['fullname'] = "%s %s" % (user.firstname, user.lastname)
        return flask.jsonify(data=data)

    return flask.jsonify(data={'error': True})


@mod.route("/logout", methods=['GET'])
def logout():
    session = flask.session
    session.pop('username', None)
    session.pop('user_fname', None)
    session.pop('user_lname', None)
    session.pop('user_id', None)

    nex = flask.request.args.get("next", "/")

    return flask.redirect(nex)
