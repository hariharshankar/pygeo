import flask

from geo.core.main import Main

mod = flask.Blueprint("type_summary", __name__)


@mod.route("/summary/type/")
@mod.route("/summary/type/<int:type_id>/<int:country_id>")
def view(type_id=None, country_id=None):

    main = Main(db)
    if not type_id or not country_id:
        url = main.get_search_redirect_url("summary/type", return_type="type_summary")
        #print(url)
        return flask.redirect(url)

    type_name = main.get_type_name(type_id)
    country_name = main.get_country_name(country_id)

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
    title = type_name + " - " + country_name
    return flask.render_template("type_summary.html",
                                 content="".join(content), title=title)
