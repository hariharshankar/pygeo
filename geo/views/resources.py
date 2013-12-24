import flask
from geo.core.moderation import Moderation

mod = flask.Blueprint("resources", __name__)


@mod.route("/resources")
def view():

    typ = flask.request.args.get("type", 0)
    country = flask.request.args.get("country", 0)

    print(typ, country)
    moderation = Moderation(db)
    keys, values = moderation.get_all_resources(country=country, typ=typ)
    baseurl = "geoid/"

    return flask.render_template("resources.html", values=values, baseurl=baseurl)
