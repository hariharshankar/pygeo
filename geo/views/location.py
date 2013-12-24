import flask
from geo.core.location import Location

mod = flask.Blueprint("location", __name__)


@mod.route("/location")
def view():

    typ = flask.request.args.get("type", 0)
    country = flask.request.args.get("country", 0)
    state = flask.request.args.get("state", 0)

    loc = Location(db)
    return flask.jsonify(data=loc.for_many_resources(typ=typ, country=country))
