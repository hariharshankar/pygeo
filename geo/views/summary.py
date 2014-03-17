import flask

from geo.core.main import Main

mod = flask.Blueprint("summary", __name__)


@mod.route("/summary")
def view():

    typ = flask.request.args.get("type", 0)
    country = flask.request.args.get("country", 0)
    #state = flask.request.args.get("state", 0)

    main = Main(db)

    type_id = main.get_type_id(typ)
    country_id = main.get_country_id(country)
    type_name = main.get_type_name(type_id)
    country_name = main.get_country_name(country_id)
    #FIXME: implement support for states

    if not country_id or not type_id:
        return flask.abort(404)

    content = []
    content.extend(["<input type='hidden'",
                    "name='summary_json'",
                    "id='summary_json'",
                    "value='" + flask.url_for("summarydata.summarydata",
                                              country_id=country_id,
                                              type_id=type_id) + "'",
                    "class='widget_urls'",
                    "/>"
                    ])
    """
    content.extend(["<input type='hidden'",
                    "name='performance_linechart_cumulative_json_url'",
                    "id='performance_linechart_cumulative_json_url'",
                    "value='" + flask.url_for("linechart.linechart",
                                              country_id=country_id,
                                              type_id=type_id,
                                              module='performance',
                                              fields='Total_Gigawatt_Hours_Generated_nbr,CO2_Emitted_(Tonnes)_nbr',
                                              chart='cumulative') + "'",
                    "class='widget_urls'",
                    "/>"
                    ])
    content.extend(["<input type='hidden'",
                    "name='unit_linechart_cumulative_json_url'",
                    "id='unit_linechart_cumulative_json_url'",
                    "value='" + flask.url_for("linechart.linechart",
                                              country_id=country_id,
                                              type_id=type_id,
                                              module='unit',
                                              fields='Capacity_(MWe)_nbr',
                                              chart='cumulative') + "'",
                    "class='widget_urls'",
                    "/>"
                    ])
    """
    title = type_name + " - " + country_name
    return flask.render_template("summary.html", content="".join(content), title=title)
