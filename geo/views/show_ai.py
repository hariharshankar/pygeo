import flask
from geo.core.geo_resource import GeoResource
from geo.db.query import Select

mod = flask.Blueprint("show_ai", __name__)
db = None


@mod.route("/show_ai/")
@mod.route("/show_ai/<string:did>/")
def view(did=None):

    if not did:
        did = flask.request.args.get("did", "")

    resource = GeoResource(db, description_id=did)

    select = Select(db)
    result = select.read("Associated_Infrastructure",
                            where=[["Parent_Plant_ID",
                                    "=",
                                    resource.parent_plant_id]]
                        )

    keys = result.column_names
    values = result.fetchall()
    html = []
    for value in values:
        ai_parent_plant_id = value[keys.index("Associated_Parent_Plant_ID")]
        ai_res = GeoResource(db, description_id=ai_parent_plant_id)
        html.append("<b><a href=\"geoid/%s\" target=\"_blank\">%s</a></b><br/>" % (ai_res.get_latest_revision_id(),
                                                                                   ai_res.get_resource_name()))

    html.append('<div id="searchAI" class="ai-search-module">')
    html.append("<div id='aiDatabase_Type' class='aiSelectable'></div>")
    html.append("<div id='aiType' class='aiSelectable'></div>")
    html.append("<div id='aiCountry' class='aiSelectable'></div>")
    html.append("<div id='aiState' class='aiSelectable'></div>")
    html.append("<div class='aiUpdateButton' id='aiUpdateButton' style='padding-top: 10px;'>")
    html.append("<button id='createAIResource' class='createAIResource'>Add Associated Infrastructure</button>")
    html.append("</div>")

    html.append("</div>")
    html.append("<div id='aiResources' class='aiSelectable' style='top: 20px;'>")
    html.append("</div>")
    return "".join(html)

