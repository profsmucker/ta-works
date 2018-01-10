# ta-works
# start-up instructions

* pip install requirements.txt
* brew install postgresql
* pg_ctl -D /usr/local/var/postgres start
* python manage.py migrate
* python manage.py runserver
