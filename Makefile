run:
	python2 manage.py runserver 0.0.0.0:8080

install:
	virtualenv --no-site-packages .
	. bin/activate
	sudo pip install -r requirements.txt

install_dev:
	virtualenv --no-site-packages .
	. bin/activate
	sudo pip install -r requirements.txt
	sudo pip install -r dev_requirements.txt
	wget http://selenium.googlecode.com/files/selenium-server-standalone-2.34.0.jar

doc:
	cd docs && make -f ./Makefile html

test:
	python2 manage.py test
