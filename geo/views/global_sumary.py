__author__ = 'harihar'

import flask

from geo.core.main import Main
from geo.db.query import Select


mod = flask.Blueprint("global_summary", __name__)
db = None

MODULE_CONTENT = """
    <table style="width: 90%">
    <tr>
        <td style="width: 70%">Number of {type_name} {db}:</td>
        <td>{total}</td>
    </tr>
    <tr>
        <td style="width: 70%">Total Cumulative Capacity (MWe):</td>
        <td>{cumulative_capacity}</td>
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
<input type='hidden' id={pie_id} class='pie_chart_values' value={pie_value} />
"""


@mod.route("/summary/global/")
def view():

    main = Main(db)
    pref = main.get_user_pref()

    modules = []
    select = Select(db)

    met = select.read("metadata")
    metadata = met.fetchall()

    module = {}
    module['heading'] = "Cumulative Capacity by Category"
    module['content'] = []
    module['content'].append("<p style='text-align: center'><b>Total Cumulative Capacity: %s MWe</b></p>"
                             % sum([t['Cumulative_Capacity'] for t in types]))
    module['content'].append("<div id='pie_chart' style='width: 900px; height: 500px;'></div>")
    module['content'] = "".join(module['content'])
    modules.append(module)

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
        s_link.append("'>Click Here</a>")

        map_link = []
        map_link.append("<a href='/map/")
        map_link.append(db_name.lower() + "/")
        map_link.append(str(t['Type_ID']) + "/")
        map_link.append(str(country_id) + "/0/")
        map_link.append("'>Map</a>")

        module = {}
        module['heading'] = type_name
        module['content'] = module_content.format(type_name=type_name,
                                                  db=dbn,
                                                  total=t['Number_of_Plants'],
                                                  cumulative_capacity=t['Cumulative_Capacity'],
                                                  summary_link="".join(s_link),
                                                  map_link="".join(map_link),
                                                  pie_id=type_name,
                                                  pie_value=t['Cumulative_Capacity'])

        modules.append(module)

    main.store_user_pref(pref[0], country_id, pref[1], pref[3])
    user_pref = main.make_html_user_pref()

    title = "Summary for " + country_name
    return flask.render_template("country_summary.html",
                                 modules=modules, title=title,
                                 country=country_name,
                                 user_pref=user_pref,
                                 body_onload="Chart.plotPieChart('', 'pie_chart')")
