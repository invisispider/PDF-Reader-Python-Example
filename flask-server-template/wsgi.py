# This is standard gunicorn driver. This is set in /etc/systemd/system/python.service
# 	to create python.sock at /var/www/html/python so the wsgi is automatic and enabled.
from application import app

if __name__ == '__main__':
    app.run(debug=True)


#TESTED: this is great. so you don't need to systemctl restart python.service
GUNICORN_CMD_ARGS="--reload"  