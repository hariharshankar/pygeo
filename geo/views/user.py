import flask
from geo.core.geo_user import GeoUser

db = None
mod = flask.Blueprint("user", __name__)


@mod.route("/login", endpoint='login', methods=['POST'])
def login():

    request = flask.request
    session = flask.session

    username = request.form['username']
    password = request.form['password']

    print(username, password)
    try:
        user = GeoUser(db, username=username)
        print(user.firstname)
    except AttributeError as e:
        print(e)
        return flask.jsonify(data={'error': True})

    if user.validate_user(password):
        session['username'] = username
        session['user_fname'] = user.firstname
        session['user_lname'] = user.lastname
        session['user_id'] = user.user_id
        session['moderator_user'] = user.moderator_user
        data = {}
        data['fullname'] = "%s %s" % (user.firstname, user.lastname)
        return flask.jsonify(data=data)

    return flask.jsonify(data={'error': True})


@mod.route("/logout", endpoint='logout', methods=['GET'])
def logout():
    session = flask.session
    session.pop('username', None)
    session.pop('user_fname', None)
    session.pop('user_lname', None)
    session.pop('user_id', None)
    session.pop('moderator_user', None)

    nex = flask.request.args.get("next", "/")

    return flask.redirect(nex)
