web: gunicorn ecommerce.wsgi
start: python manage.py runserver -h 0.0.0.0 -p ${PORT}
init: python manage.py db init
makemigrations: python manage.py makemigrations
migrate: python manage.py migrate

