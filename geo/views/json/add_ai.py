import flask
from geo.core.geo_resource import GeoResource

mod = flask.Blueprint("add_ai", __name__)
db = None


@mod.route("/add_ai", endpoint="add_ai")
def view():

    vals = {}
    vals["did"] = flask.request.args.get("did", 0)
    vals["assid"] = flask.request.args.get("assid", 0)

    if not int(vals["did"]) > 0 or not int(vals["assid"]) > 0:
        return

    session = db.session

    gr = GeoResource(db, vals["did"])
    vals["ppid"] = gr.parent_plant_id
    vals["typ"] = gr.type_id

    assgr = GeoResource(db, vals["assid"])
    vals["assppid"] = assgr.parent_plant_id
    vals["asstypeid"] = assgr.type_id
    vals["asscountryid"] = assgr.country_id
    vals["assstateid"] = assgr.state_id

    if not int(vals["ppid"]) > 0 and not int(vals["assppid"]) > 0:
        return

    sql = "INSERT INTO Associated_Infrastructure SET " \
          "`Parent_Plant_ID`=:ppid," \
          "`Type_ID`=:typ," \
          "`Associated_Parent_Plant_ID`=:assppid," \
          "`Associated_Type_ID`=:asstypeid," \
          "`Associated_Country_ID`=:asscountryid," \
          "`Associated_State_ID`=:assstateid"

    try:
        session.execute(sql, vals)
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

    return "Success"