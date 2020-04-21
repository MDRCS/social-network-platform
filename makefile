## command are : make build | make run

define USAGE
-> build system ⚙️

Commands:

	@echo "    make init       # Install Flask-app dependencies with virtualenv"
	@echo "    make serve      # Starts a Flask development server locally."
	@echo "    make shell      # Runs 'manage.py shell' locally with iPython."
	@echo "    make celery     # Runs one development Celery worker with Beat."
	@echo "    make style      # Check code styling with flake8."
	@echo "    make lint       # Runs PyLint."
	@echo "    make test       # Tests entire application with pytest."

endef

export USAGE

help:
	@echo "$$USAGE"

init:
	virtualenv -p python3 venv
	source ./venv/bin/activate
	pip install -r requirements.txt
	mkdir data
    mkdir log
    chmod -R 755 mongo_restart
    mongod -f mongod.conf

shell:
	source ./venv/bin/activate
	python manage.py shell

test:
	export environment=testing
	export MONGODB_NAME=social-network-test
	python tests.py

coverage:
	coverage run --omit venv/* tests.py
	coverage report

serve:
	export environment=development
	python manage.py runserver

all: init test serve
