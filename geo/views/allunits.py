import flask

from geo.core.main import Main
from geo.core.moderation import Moderation
from geo.core.geo_resource import GeoResource
from geo.serializations.html import Html


mod = flask.Blueprint("allunits", __name__)
db = None


@mod.route("/allunits/")
@mod.route("/allunits/<string:db_type>/<int:type_id>/<int:country_id>")
@mod.route("/allunits/<string:db_type>/<int:type_id>/<int:country_id>/<int:state_id>")
def view(db_type=None, type_id=None, country_id=None, state_id=None):

    main = Main(db)
    pref = main.get_user_pref()
    if not type_id or not country_id:
        url = "/".join(["/allunits", pref[0], pref[1], pref[2]])
        #url = main.get_search_redirect_url("summary/type", return_type="type_summary")
        #print(url)
        return flask.redirect(url)

    type_name = main.get_type_name(type_id)
    country_name = main.get_country_name(country_id)

    units = []
    moderation = Moderation(db)
    res_label, resources = moderation.get_all_resources(country_id=country_id, type_id=type_id)
    for res in resources:
        desc_id = res[0]
        name = res[1]
        unit = {"resource_name": name, "resource_id": desc_id}
        geo_resource = GeoResource(db, desc_id)
        html = Html(geo_resource)
        html.editable = False
        unit["content"] = html.make_unit_module("Unit_Description")
        units.append(unit)

    main.store_user_pref(pref[0], country_id, type_id, pref[3])
    user_pref = main.make_html_user_pref()

    return flask.render_template("allunits.html",
                                 resources=units,
                                 country=country_name,
                                 type=type_name,
                                 user_pref=user_pref)
