import flask

mod = flask.Blueprint("map", __name__)


@mod.route("/map", endpoint="map")
def view():

    typ = flask.request.args.get("type", "")
    country = flask.request.args.get("country", 0)
    state = flask.request.args.get("state", 0)
    map_url = flask.url_for("location.location", _external=True, country=country, type=typ, state=state)

    return flask.render_template("map.html", map_url=map_url)
