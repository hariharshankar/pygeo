import flask

from geo.core.main import Main
from geo.db.query import Select


mod = flask.Blueprint("country_summary", __name__)


@mod.route("/summary/country/")
@mod.route("/summary/country/<int:country_id>")
def view(country_id=None):

    main = Main(db)
    if not country_id:
        url = main.get_search_redirect_url("summary/country",
                                           return_type='country_summary')
        return flask.redirect(url)

    country_name = main.get_country_name(country_id)

    modules = []
    select = Select(db)

    res = select.read("metadata",
                      columns=["Type_ID",
                               "Number_of_Plants",
                               "Cumulative_Capacity"],
                      where=[["Country_ID", "=", country_id]],
                      order_by=["Type_ID", "asc"])
    types = res.fetchall()

    module_content = """
    <table style="width: 90%">
    <tr>
        <td style="width: 70%">Number of {type_name} {db}:</td>
        <td>{total}</td>
    </tr>
    <tr>
        <td style="width: 70%">Map All {type_name} {db}:</td>
        <td>{map_link}</td>
    </tr>
    <tr>
        <td style="width: 70%">Complete summary:</td>
        <td>{summary_link}</td>
    </tr>
</table>
"""

    #keys, types = main.get_types_for_country(country_id)
    for t in types:
        type_name = main.get_type_name(t['Type_ID']).replace("_", " ")

        db_name = main.get_databases(type_id=t['Type_ID'])[1][0][0]
        dbn = ""
        if db_name == "PowerPlants":
            dbn = "power plants"
        else:
            dbn = ""

        s_link = []
        s_link.append("<a href='/summary/type/")
        s_link.append(str(t['Type_ID']))
        s_link.append("/" + str(country_id))
        s_link.append("' target='_blank'>Click Here</a>")

        map_link = []
        map_link.append("<a href='/map/")
        map_link.append(db_name.lower() + "/")
        map_link.append(str(t['Type_ID']) + "/")
        map_link.append(str(country_id) + "/0/")
        map_link.append("' target='_blank'>Map</a>")

        module = {}
        module['heading'] = type_name
        module['content'] = module_content.format(type_name=type_name,
                                                  db=dbn,
                                                  total=t['Number_of_Plants'],
                                                  summary_link="".join(s_link),
                                                  map_link="".join(map_link))

        modules.append(module)

    title = "Summary for " + country_name
    return flask.render_template("country_summary.html",
                                 modules=modules, title=title)
