import flask
from geo.core.location import Location

mod = flask.Blueprint("location", __name__)
db = None


@mod.route("/location", endpoint="location")
def view():

    typ = flask.request.args.get("type", 0)
    country = flask.request.args.get("country", 0)
    state = flask.request.args.get("state", 0)
    description_id = flask.request.args.get("description_id", 0)

    loc = Location(db)
    if description_id > 0:
        return flask.jsonify(data=loc.for_one_resource(description_id=description_id))
    else:
        return flask.jsonify(data=loc.for_many_resources(type_id=typ, country_id=country))
