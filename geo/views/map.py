import flask

mod = flask.Blueprint("map", __name__)


@mod.route("/map", endpoint="map")
def view():

    typ = flask.request.args.get("type", "")
    country = flask.request.args.get("country", 0)
    state = flask.request.args.get("state", 0)

    return flask.render_template("map.html", country=country, typ=typ, state=state)
