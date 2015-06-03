import flask
from geo.core.geo_resource import GeoResource
from geo.core.main import Main


mod = flask.Blueprint("form", __name__)
db = None


@mod.route("/create_resources/")
@mod.route("/form.php")
@mod.route("/geoid/<int:description_id>", endpoint='factsheet')
def view(description_id=None):

    if not description_id:
        description_id = flask.request.args.get("pid", 0)

    geo_resource = None
    prefs = None

    main = Main(db)
    if int(description_id) == 0:
        prefs = main.get_user_pref()
        geo_resource = GeoResource(db, description_id, type_id=prefs[1], country_id=prefs[2], state_id=prefs[3])
    else:
        geo_resource = GeoResource(db, description_id)

    html = geo_resource.generate_editable()
    title = geo_resource.get_resource_name(geo_resource.type_name)
    if not title:
        title = "New %s %s" % (main.get_type_name(prefs[1]), prefs[0])
    user_pref = main.make_html_user_pref()
    return flask.render_template("form.html", modules=html, title=title,
                                 user_pref=user_pref,
                                 is_moderated=geo_resource.is_moderated if description_id > 0 else True)
