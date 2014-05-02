import flask
from geo.core.geo_resource import GeoResource
from geo.core.main import Main


mod = flask.Blueprint("form", __name__)
db = None


@mod.route("/form.php", alias=True)
@mod.route("/geoid/<int:description_id>", endpoint='factsheet')
def view(description_id):

    if not description_id:
        description_id = flask.request.args.get("pid", 0)

    geo_resource = GeoResource(db, description_id)

    html = geo_resource.generate_editable()
    title = geo_resource.get_resource_name(geo_resource.type_name)
    main = Main(db)
    user_pref = main.make_html_user_pref()
    return flask.render_template("form.html", modules=html, title=title,
                                 user_pref=user_pref)
