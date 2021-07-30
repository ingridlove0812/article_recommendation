from app import app
from flaskext.mysql import MySQL
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'user'
app.config['MYSQL_DATABASE_PASSWORD'] = 'password'
app.config['MYSQL_DATABASE_DB'] = 'MartServer'
app.config['MYSQL_DATABASE_HOST'] = 'xxx.xxx.xxx.xxx'
mysql.init_app(app)
