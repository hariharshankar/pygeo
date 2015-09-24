"""
Registering all the views in flask.
Includes both html and json end points.
"""

import flask
from geo.db import connection
import geo.views.form as form
import geo.views.resources as resources
import geo.views.new_resources as new_resources
import geo.views.moderation as moderation
import geo.views.moderation_submit as moderationsubmit
import geo.views.map
import geo.views.form_submit as formsubmit
import geo.views.type_summary as type_summary
import geo.views.country_summary as country_summary
import geo.views.user as user
import geo.views.index as index

# json services
import geo.views.json.location as location
import geo.views.json.menu as menu
import geo.views.json.summarydata as summarydata
import geo.views.json.linechart as linechart
import geo.views.json.get_resources as get_resources
import geo.views.json.add_ai as add_ai
import geo.views.show_ai as show_ai
import geo.views.allunits as allunits

# static html
import geo.views.static.partners as partners

app = flask.Flask(__name__)
app.secret_key = '\xe1\xf1\x91\x1a8\xd5\xbf\xe2\x84f\xff\xd1D\x9d\x08Q\xff.$#\x1a\x08PNU\r>(\xb5\x92a\x87\xbf\xca3\xc9F\xec\xe3\x06aQ0\x19\xb1\xbf\xd0\xae\x8b\x8a5\xfbW\xab\x18\x08uV\x94)\xa0\x99\xfb\x0b1\x0f\xa2n\xba\xa3mya\xf8\xdfR\'F@\xd9\xb2\x10S\xf4r~\xae\x94\x1c\x7f\xd1J\x86\x1ar.m"\xdc\x18\x85\x80\xb8\x18\x1cG\x81\x1e]\xb3E\x01i\xf4\xd9_\x18\xfar\xbe`\xaa\xa7+3\x92\xe8Q'
#app.config['SERVER_NAME'] = "http://globalenergyobservatory.org/dev"

conn = connection.Db()

form.db = conn
resources.db = conn
new_resources.db = conn
menu.db = conn
geo.views.map.db = conn
location.db = conn
formsubmit.db = conn
type_summary.db = conn
country_summary.db = conn
summarydata.db = conn
linechart.db = conn
user.db = conn
index.db = conn
moderation.db = conn
moderationsubmit.db = conn
get_resources.db = conn
add_ai.db = conn
show_ai.db = conn
allunits.db = conn

# html
app.register_blueprint(form.mod)
app.register_blueprint(resources.mod)
app.register_blueprint(new_resources.mod)
app.register_blueprint(moderation.mod)
app.register_blueprint(geo.views.map.mod)
app.register_blueprint(formsubmit.mod)
app.register_blueprint(type_summary.mod)
app.register_blueprint(country_summary.mod)
app.register_blueprint(user.mod)
app.register_blueprint(index.mod)
app.register_blueprint(moderationsubmit.mod)
app.register_blueprint(add_ai.mod)
app.register_blueprint(show_ai.mod)
app.register_blueprint(allunits.mod)

# json services
app.register_blueprint(summarydata.mod)
app.register_blueprint(location.mod)
app.register_blueprint(menu.mod)
app.register_blueprint(linechart.mod)
app.register_blueprint(get_resources.mod)

# static html
app.register_blueprint(partners.mod)