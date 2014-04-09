import flask
from geo.db import connection
import geo.views.form as form
import geo.views.resources as resources
import geo.views.search as search
import geo.views.map
import geo.views.form_submit as formsubmit
import geo.views.summary as summary
import geo.views.user as user
import geo.views.index as index

# json services
import geo.views.json.location as location
import geo.views.json.menu as menu
import geo.views.json.summarydata as summarydata
import geo.views.json.linechart as linechart

app = flask.Flask(__name__)
app.secret_key = '\xe1\xf1\x91\x1a8\xd5\xbf\xe2\x84f\xff\xd1D\x9d\x08Q\xff.$#\x1a\x08PNU\r>(\xb5\x92a\x87\xbf\xca3\xc9F\xec\xe3\x06aQ0\x19\xb1\xbf\xd0\xae\x8b\x8a5\xfbW\xab\x18\x08uV\x94)\xa0\x99\xfb\x0b1\x0f\xa2n\xba\xa3mya\xf8\xdfR\'F@\xd9\xb2\x10S\xf4r~\xae\x94\x1c\x7f\xd1J\x86\x1ar.m"\xdc\x18\x85\x80\xb8\x18\x1cG\x81\x1e]\xb3E\x01i\xf4\xd9_\x18\xfar\xbe`\xaa\xa7+3\x92\xe8Q'
#app.config['SERVER_NAME'] = "http://globalenergyobservatory.org/dev"

conn = connection.Db()

form.db = conn
resources.db = conn
menu.db = conn
geo.views.map.db = conn
location.db = conn
formsubmit.db = conn
summary.db = conn
summarydata.db = conn
linechart.db = conn
user.db = conn
index.db = conn

# html
app.register_blueprint(form.mod)
app.register_blueprint(resources.mod)
app.register_blueprint(search.mod)
app.register_blueprint(geo.views.map.mod)
app.register_blueprint(formsubmit.mod)
app.register_blueprint(summary.mod)
app.register_blueprint(user.mod)
app.register_blueprint(index.mod)

# json services
app.register_blueprint(summarydata.mod)
app.register_blueprint(location.mod)
app.register_blueprint(menu.mod)
app.register_blueprint(linechart.mod)