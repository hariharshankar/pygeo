import flask
from geo.core.main import Main

mod = flask.Blueprint("menu", __name__)


@mod.route("/menu", endpoint="menu")
def view():

    db_name = flask.request.args.get("database_type", "")
    typ = flask.request.args.get("type", 0)
    country = flask.request.args.get("country", 0)
    state = flask.request.args.get("state", 0)

    return_type = flask.request.args.get("return_type", "")

    if not return_type:
        #FIXME: return 404
        flask.abort(404)

    return_type = return_type.lower()
    main = Main(db)

    keys = []
    values = []
    if return_type == "database_type":
        keys, values = main.get_databases()
    elif return_type == "type":
        if not db_name:
            db_name = "PowerPlants"
        keys, values = main.get_types(db_name)
    elif return_type == "country":
        if not typ:
            flask.abort(404)
            #FIXME: 404
        keys, values = main.get_countries(typ)
    elif return_type == "state":
        if not country:
            flask.abort(404)
            #FIXME: 404
        keys, values = main.get_states(country)
        values.insert(0, [0, "All"])


    return flask.jsonify(keys=keys, values=values)
