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

init-3.6.7:
		brew install pyenv
		brew upgrade pyenv-virtualenv
		pyenv versions
		pyenv install  3.6.7
		pyenv virtualenvs
		pyenv global 3.6.7
		pyenv local 3.6.7
		source /Users/MDRAHALI/.pyenv/versions/3.6.7/envs/venv-3.6.7/bin/activate
		export environment=default
		export FLASK_APP=manage.py
		flask run

shell:
	source ./venv/bin/activate
	export FLASK_APP=manage.py
	flask shell

shell-3.6.7:
		source /Users/MDRAHALI/.pyenv/versions/3.6.7/envs/venv-3.6.7/bin/activate
		export environment=default
		export FLASK_APP=manage.py
		flask shell

test:
	export environment=testing
	export MONGODB_NAME=social-network-test
	python tests.py

coverage:
	coverage run tests.py
	coverage report

serve:

	source /Users/MDRAHALI/.pyenv/versions/3.6.7/envs/venv-3.6.7/bin/activate
	export environment=development
	export FLASK_APP=manage.py
	flask run

all: init test serve
