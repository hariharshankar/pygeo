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
        return flask.redirect(url)

    moderation = Moderation(db)
    keys, values = moderation.get_all_resources(country_id=country, type_id=typ, state_id=state)
    baseurl = "/geoid/"

    # storing the prefs to a cookie
    main.store_user_pref(db_type, country, typ, state)

    type_name = main.get_type_name(typ)
    country_name = main.get_country_name(country)
    state_name = None
    if state > 0:
        state_name = main.get_state_name(state)

    user_pref = main.make_html_user_pref()

    return flask.render_template("resources.html",
                                 values=values, baseurl=baseurl,
                                 user_pref=user_pref, type=type_name, country=country_name,
                                 state=state_name if state > 0 else False,
                                 category=db_type)
