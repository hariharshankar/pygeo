import flask
from geo.db.query import Select

mod = flask.Blueprint("summarydata", __name__)
db = None


@mod.route("/summarydata", endpoint="summarydata")
def view():

    type_id = flask.request.args.get("type_id", 0)
    country_id = flask.request.args.get("country_id", 0)
    #state_id = flask.request.args.get("state_id", 0)

    if not type_id and not country_id:
        flask.abort(404)

    where = [["Country_ID", "=", country_id]]
    columns = []
    if type_id > 0:
        where.append(["AND"])
        where.append(["Type_ID", "=", type_id])
    else:
        columns.extend(["Type_ID", "Country_ID", "Number_of_Plants", "Cumulative_Capacity"])

    select = Select(db)
    result = select.read("metadata", columns=columns, where=where)

    keys, values = select.process_result_set(result)

    return flask.jsonify(data={'keys': keys, 'values': values})
