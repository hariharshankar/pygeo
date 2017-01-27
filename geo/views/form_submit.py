import flask
from geo.core.geo_resource import GeoResource
from geo.db.insert import InsertFactSheet
from geo.db.query import Select

mod = flask.Blueprint("formsubmit", __name__)
db = None

@mod.route("/formsubmit", methods=['POST'], endpoint="formsubmit")
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
    form_data["User_ID"] = flask.session['user_id']
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
    modules = res_modules.fetchone()
    print(modules)
    features = list(modules['Features'])
    features.remove("Annual_Performance")
    features.append("Annual_Performance")

    for f in features:

        table_name = geo_resource.type_name + "_" + f

        if f.startswith("Unit_Description") or\
                f.startswith("Environmental_Issues") or \
                f.startswith("Comments") or \
                f.startswith("References") or \
                f.startswith("Upgrades"):
            insert.insert(table_name, form_data, "row_columns", description_id)
        elif f == "Annual_Performance":
            if geo_resource.type_id == 5:
                cap_gen_table_name = "Nuclear_Capacity_Generated"
                gwh_table_name = "Nuclear_Gigawatt_Hours_Generated"
                insert.insert(cap_gen_table_name, form_data, "nuclear_performance", description_id)
                insert.insert(gwh_table_name, form_data, "nuclear_performance", description_id)
            insert.insert(table_name, form_data, "performance", description_id)
        elif f == "Location":
            insert.insert(table_name, form_data, "generic", description_id)
            insert.insert(geo_resource.type_name + "_Overlays", form_data, "row_columns", description_id)
        elif f == "Identifiers" or f == "Dual_Node_Identifiers" or f == "Dual_Node_Locations":
                continue
        elif f == "History":
                continue
        elif f == "Owner_Details":
            insert.insert(geo_resource.type_name + "_Owners", form_data, "row_columns", description_id)
            insert.insert(table_name, form_data, "generic", description_id)
        elif f == "Description":
            insert.insert(table_name, form_data, "generic", description_id)
            if geo_resource.type_id == 11:
                insert.insert(geo_resource.type_name + "_Contaminants", form_data, "enum_table", description_id)
        elif f == "Dual_Node_Description":
            connection_id = insert.insert(geo_resource.type_name + "_Connection_Description",
                                          form_data, "generic")
            station_1_id = insert.insert(geo_resource.type_name + "_Station_Description",
                                         form_data, "generic", dual=1)
            station_2_id = insert.insert(geo_resource.type_name + "_Station_Description",
                                         form_data, "generic", dual=2)
            print(connection_id, station_1_id, station_2_id)
            insert.insert_dual_node_description(geo_resource.type_name + "_Description", form_data, description_id,
                                                station_1_id, station_2_id, connection_id)
        elif f != "Associated_Infrastructure":
            insert.insert(table_name, form_data, "generic", description_id)

    #return flask.render_template("form.html", modules=html, title=title)
    flask.flash("Your changes were successfully submitted and is awaiting moderation.<br/>\
          Link to <a href='" +
          flask.url_for('form.factsheet', description_id=old_description_id) +
          "'>Original FactSheet</a>", "warning")
    return flask.redirect(flask.url_for('form.factsheet', description_id=description_id))
