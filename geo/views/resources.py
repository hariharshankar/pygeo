import flask
from geo.core.moderation import Moderation
from geo.core.main import Main

db = None
mod = flask.Blueprint("resources", __name__)


@mod.route("/resources/")
@mod.route("/resources/<string:db_type>/<int:typ>/<int:country>/<int:state>")
def view(db_type=None, typ=None, country=None, state=None):

    if not typ or not country:
        typ = flask.request.args.get("type", 0)
        country = flask.request.args.get("country", 0)
        state = flask.request.args.get("state", 0)


    main = Main(db)

    if not typ or not country:
        pref = main.get_user_pref()
        url_comp = ["/resources"]
        url_comp.extend(pref)
        url = "/".join(url_comp)
        #url = main.get_search_redirect_url("resources")
        return flask.redirect(url)

    moderation = Moderation(db)
    keys, values = moderation.get_all_resources(country=country, typ=typ)
    baseurl = "/geoid/"

    # storing the prefs to a cookie
    main.store_user_pref(db_type, country, typ, state)

    user_pref = main.make_html_user_pref()

    return flask.render_template("resources.html",
                                 values=values, baseurl=baseurl,
                                 user_pref=user_pref)
