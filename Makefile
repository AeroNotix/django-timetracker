run:
	python2 manage.py runserver 0.0.0.0:8080

install:
	virtualenv --no-site-packages .
	pip install -r requirements.txt

doc:
	cd docs && make -f ./Makefile html

test:
	python2 manage.py test
