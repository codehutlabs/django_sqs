# Convenience makefile to build the dev env and run common commands
# This example is for a virtualenv-based django project
# Based on https://github.com/niteoweb/Makefile

.PHONY: all
all: .installed

.PHONY: install
install:
	@rm -f .installed  # force re-install
	@make .installed

.installed: requirements.txt djangosqs_backup djangosqs_media djangosqs_static
	@echo "requirements.txt is newer than .installed, (re)installing"
	@virtualenv -p python3.7 venv
	@venv/bin/pip install -r requirements-dev.txt
	@venv/bin/pre-commit install -f --hook-type pre-commit
	@venv/bin/pre-commit install -f --hook-type pre-push
	@echo "This file is used by 'make' for keeping track of last install time. If requirements.txt is newer then this file (.installed) then all 'make *' commands that depend on '.installed' know they need to run." \
		> .installed
	@cp djangosqs/local_settings.txt djangosqs/local_settings.py

djangosqs_backup:
	@mkdir djangosqs_backup

djangosqs_media:
	@mkdir djangosqs_media
	@mkdir djangosqs_media/uploads
	@mkdir djangosqs_media/receipt

djangosqs_static:
	@mkdir djangosqs_static

.PHONY: collectstatic
collectstatic:
	@venv/bin/python manage.py collectstatic --noinput

.PHONY: migrate
migrate:
	@venv/bin/python manage.py migrate

.PHONY: load
load:
	@venv/bin/python manage.py loaddata orderapizza.json
	@echo Copying images to media folder
	@rsync -rupE djangosqs/static/images/ djangosqs_media/uploads/

.PHONY: run
run:
	@venv/bin/python manage.py runserver

.PHONY: clean
clean:
	@rm -rf venv/ htmlcov/
	@rm -f .installed .coverage

.PHONY: test
test: djangosqs_local_settings
