import flask
from geo.core.geo_resource import GeoResource


mod = flask.Blueprint("form", __name__)


@mod.route("/form.php", alias=True)
@mod.route("/geoid/<int:description_id>", endpoint='factsheet')
def view(description_id):

    if not description_id:
        description_id = flask.request.args.get("pid", 0)

    geo_resource = GeoResource(db, description_id)

    html = geo_resource.generate_editable()
    title = geo_resource.get_resource_name(geo_resource.type_name)
    return flask.render_template("form.html", modules=html, title=title)
