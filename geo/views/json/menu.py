import flask
from geo.core.main import Main

mod = flask.Blueprint("menu", __name__)
db = None


@mod.route("/menu", endpoint="menu")
def view():

    main = Main(db)
    pref = main.get_user_pref()

    new_resource = flask.request.args.get("new_resource", False)
    if new_resource == "true":
        new_resource = True
    else:
        new_resource = False

    db_name = flask.request.args.get("database_type", pref[0])
    typ = flask.request.args.get("type", pref[1])
    country = flask.request.args.get("country", pref[2])
    state = flask.request.args.get("state", pref[3])

    return_type = flask.request.args.get("return_type", "")

    if not return_type:
        flask.abort(404)
        return

    return_type = return_type.lower()

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
            return
        keys, values = main.get_countries(typ, new_resource=new_resource)
    elif return_type == "state":
        if not country:
            flask.abort(404)
            return
        keys, values = main.get_states(country, new_resource=new_resource)
        values.insert(0, [0, "All"])

    return flask.jsonify(keys=keys, values=values)
