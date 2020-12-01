.PHONY: clean clean-build clean-pyc clean-out docs help
.DEFAULT_GOAL := help

help:
	@ echo
	@ echo '  Usage:'
	@ echo ''
	@ echo '    make <target> [flags...]'
	@ echo ''
	@ echo '  Targets:'
	@ echo ''
	@ awk '/^#/{ comment = substr($$0,3) } comment && /^[a-zA-Z][a-zA-Z0-9_-]+ ?:/{ print "   ", $$1, comment }' $(MAKEFILE_LIST) | column -t -s ':' | sort
	@ echo ''
	@ echo '  Flags:'
	@ echo ''
	@ awk '/^#/{ comment = substr($$0,3) } comment && /^[a-zA-Z][a-zA-Z0-9_-]+ ?\?=/{ print "   ", $$1, $$2, comment }' $(MAKEFILE_LIST) | column -t -s '?=' | sort
	@ echo ''

## build the python virtual env for the project
venv:  clean
	bin/quick_start.sh

## make clean
clean: clean-build clean-pyc clean-out

## remove build artifacts
clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

## remove python file artifacts
clean-pyc:
	find . -name '__pycache__' -exec rm -rf {} +

## remove hydra outputs
clean-out:
	rm -rf outputs/ .pytest_cache/ asyncweb_epoch_*.ckpt

## start the services inside docker
start:
	bin/start_server.sh

## start the services inside docker
stop:
	docker-compose down && docker system prune -f

## start the services inside docker
start_local:
	bin/start_local.sh

## check style with flake8
lint: lint-asyncweb lint-tests

## check asyncweb style with flake8
lint-asyncweb:
	flake8 asyncweb

## check tests style with flake8
lint-tests:
	flake8 tests

## build docker image
build_image:
	bin/build_image.sh

## build source and wheel package
dist: clean 
	python setup.py sdist bdist_wheel

## install the package to active site
install: clean 
	pip install .

## uninstall package from active site
uninstall: clean
	pip uninstall asyncweb

## run tests in tox envs
test:
	#docker stop $(MONGODB_CONTAINER_NAME) || true
	#docker run -d --rm --name $(MONGODB_CONTAINER_NAME) -p 27017:27017 mongo:4.2
	pytest -sv --cov=fastapi_users/ --cov-report=term-missing
	#docker stop $(MONGODB_CONTAINER_NAME)

## helper for renaming
find: 
	@read -p "Enter Term: " term; \
	grep -rnw ./ -e "$$term"

format:
	black --skip-string-normalization --line-length 100 src test
