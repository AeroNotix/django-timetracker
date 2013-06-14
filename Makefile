run:
	python2 manage.py runserver 0.0.0.0:8080

doc:
	cd docs && make -f ./Makefile html	
