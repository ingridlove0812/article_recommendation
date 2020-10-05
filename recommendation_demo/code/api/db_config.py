from app import app
from flaskext.mysql import MySQL
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'TVBS_NM'
app.config['MYSQL_DATABASE_PASSWORD'] = 'frNsX7V@P@4mRg#8'
app.config['MYSQL_DATABASE_DB'] = 'MartServer'
app.config['MYSQL_DATABASE_HOST'] = '10.33.0.3'
mysql.init_app(app)