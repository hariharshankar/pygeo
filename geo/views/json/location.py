import flask
from geo.core.location import Location
from geo.core.main import Main


mod = flask.Blueprint("location", __name__)
db = None


@mod.route("/location", endpoint="location")
def view():

    typ = flask.request.args.get("type", 0)
    country = flask.request.args.get("country", 0)
    state = flask.request.args.get("state", 0)
    description_id = flask.request.args.get("description_id", 0)

    loc = Location(db)
    try:
        desc_id = int(description_id)
    except ValueError:
        desc_id = 0

    if desc_id > 0:
        return flask.jsonify(data=loc.for_one_resource(description_id=description_id))
    elif typ > 0 and country > 0:
        return flask.jsonify(data=loc.for_many_resources(type_id=typ, country_id=country))
    else:
        bound_location = None
        main = Main(db)
        prefs = main.get_user_pref()
        country_name = main.get_country_name(prefs[2])
        state_name = main.get_state_name(prefs[3])
        bound_location = "%s, %s" % (state_name, country_name)
        return flask.jsonify(data={"boundLocation": bound_location})
