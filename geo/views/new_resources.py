import flask
from geo.core.moderation import Moderation
from geo.core.main import Main

db = None
mod = flask.Blueprint("new_resources", __name__)


@mod.route("/new_resources/")
def view(db_type=None, typ=None, country=None, state=None):

    """
    if not typ or not country or not state:
        # TODO handle error with message
        return flask.abort(404)

    main = Main(db)

    if not typ or not country:
        pref = main.get_user_pref()
        url_comp = ["/new_resources"]
        url_comp.extend(pref)
        url = "/".join(url_comp)
        #url = main.get_search_redirect_url("resources")
        return flask.redirect(url)

    moderation = Moderation(db)
    keys, values = moderation.get_all_resources(country_id=country, type_id=typ)
    baseurl = "/geoid/"

    # storing the prefs to a cookie
    main.store_user_pref(db_type, country, typ, state)

    type_name = main.get_type_name(typ)
    country_name = main.get_country_name(country)
    state_name = None
    if state > 0:
        state_name = main.get_state_name(state)

    user_pref = main.make_html_user_pref()
    """
    return flask.render_template("new_resources.html")
