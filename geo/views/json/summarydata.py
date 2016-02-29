import flask
from geo.db.query import Select
import json

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
    if int(type_id) > 0:
        where.append(["AND"])
        where.append(["Type_ID", "=", type_id])
    else:
        columns.extend(["Type_ID", "Country_ID", "Number_of_Plants", "Cumulative_Capacity"])

    select = Select(db)
    result = select.read("metadata", columns=columns, where=where, dict_cursor=False)

    keys = result.column_names
    values = []
    if not result.with_rows:
        return flask.jsonify({'keys': keys, 'values': values})

    rows = result.fetchall()
    for r in rows[0]:
        r = r.decode("utf8")
        print(r, type(r))
        values.append(json.loads(r))
    #values = [json.loads(str(r)) for r in rows]
    #keys, values = select.process_result_set(result)

    data = {'keys': keys, 'values': values}

    return flask.jsonify(data)
