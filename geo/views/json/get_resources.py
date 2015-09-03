import flask
from geo.core.moderation import Moderation
from geo.core.main import Main


mod = flask.Blueprint("get_resources", __name__)
db = None


@mod.route("/get_resources", endpoint="get_resources")
def view():

    typ = flask.request.args.get("type", 0)
    country = flask.request.args.get("country", 0)
    state = flask.request.args.get("state", 0)

    mod = Moderation(db)

    keys, values = mod.get_all_resources(country_id=country, type_id=typ)

    res = []
    for v in values:
        val = {}
        for i, k in enumerate(keys):
            val[k] = v[i]
        res.append(val)
    return flask.jsonify(resources=res)
