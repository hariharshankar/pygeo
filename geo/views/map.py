import flask
from geo.core.main import Main

mod = flask.Blueprint("map", __name__)


@mod.route("/map/")
@mod.route("/map/<string:db_type>/<int:typ>/<int:country>/<int:state>/")
def view(db_type=None, typ=None, country=None, state=None):

    if not typ or not country:
        typ = flask.request.args.get("type", "")
        country = flask.request.args.get("country", 0)
        state = flask.request.args.get("state", 0)

    main = Main(db)
    if not typ or not country:
        url = main.get_search_redirect_url("map")
        return flask.redirect(url)

    main.store_user_pref(db_type, country, typ, state)
    map_url = flask.url_for("location.location", _external=True, country=country, type=typ, state=state)

    return flask.render_template("map.html", map_url=map_url)
