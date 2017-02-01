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
          "`Parent_Plant_ID`=%(ppid)s," \
          "`Type_ID`=%(typ)s," \
          "`Associated_Parent_Plant_ID`=%(assppid)s," \
          "`Associated_Type_ID`=%(asstypeid)s," \
          "`Associated_Country_ID`=%(asscountryid)s," \
          "`Associated_State_ID`=%(assstateid)s"

    db_conn = db.session
    session = db_conn.cursor(dictionary=True)

    try:
        session.execute(sql, vals)
        db_conn.commit()
    except:
        db_conn.rollback()
        raise
    finally:
        db_conn.close()

    return "Success"