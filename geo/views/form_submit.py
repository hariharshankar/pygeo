import flask
from geo.core.geo_resource import GeoResource
from geo.db.insert import InsertFactSheet
from geo.db.query import Select

mod = flask.Blueprint("formsubmit", __name__)

@mod.route("/formsubmit", methods=['POST'])
def view():

    request = flask.request
    if not request.form:
        # FIXME: ERROR
        flask.abort(406)
        return

    form_data = request.form.copy()
    insert = InsertFactSheet(db)
    #description_id = insert.insert("History", form_data, "history")
    #insert.insert("Coal_Description", form_data, "generic", description_id)

    result = ""

    old_description_id = form_data.get("Description_ID")

    parent_plant_id = 0
    if int(old_description_id) > 0:

        geo_resource = GeoResource(db, old_description_id)
        parent_plant_id = geo_resource.parent_plant_id


    form_data["Moderated"] = "0"
    form_data["Moderator_ID"] = "0"
    form_data["Accepted"] = "0"
    form_data["User_ID"] = "11"
    form_data["Parent_Plant_ID"] = str(parent_plant_id)

    description_id = insert.insert("History", form_data, "history")
    #form_data["Description_ID"] = description_id

    geo_resource = GeoResource(db, description_id)

    if not geo_resource:
        return flask.abort(404)

    select = Select(db)
    res_modules = select.read("Type_Features",
                                    where=[["Type_ID", "=", geo_resource.type_id]]
                                    )
    modules = res_modules.first()

    for f in modules.Features.split(","):
        module_id = f

        table_name = geo_resource.type_name + "_" + f

        if f.startswith("Unit_Description") or\
                f.startswith("Environmental_Issues") or \
                f.startswith("Comments") or \
                f.startswith("References") or \
                f.startswith("Upgrades"):
            insert.insert(table_name, form_data, "row_columns", description_id)
        elif f == "Annual_Performance":
            insert.insert(table_name, form_data, "performance", description_id)
        elif f == "Location":
            insert.insert(table_name, form_data, "generic", description_id)
            insert.insert(geo_resource.type_name + "_Overlays", form_data, "row_columns", description_id)
        elif f == "Identifiers":
                continue
        elif f == "History":
                continue
        elif f == "Owner_Details":
            insert.insert(geo_resource.type_name + "_Owners", form_data, "row_columns", description_id)
            insert.insert(table_name, form_data, "generic", description_id)
        elif f != "Associated_Infrastructure":
            insert.insert(table_name, form_data, "generic", description_id)

    #return flask.render_template("form.html", modules=html, title=title)
    flask.flash("Your changes were successfully submitted and is awaiting moderation.<br/>\
          Link to <a href='" +
          flask.url_for('form.factsheet', description_id=old_description_id) +
          "' target='_blank'>Original FactSheet</a>", "warning")
    return flask.redirect(flask.url_for('form.factsheet', description_id=description_id))
