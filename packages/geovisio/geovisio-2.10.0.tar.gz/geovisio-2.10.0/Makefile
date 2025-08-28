.DEFAULT_GOAL := help

.PHONY: run-all-compose

run-all-compose:  ## Run all services with docker compose
	docker-compose -f docker/docker-compose-full.yml up

fmt:	## Run code formatting
	black .

generate-swagger:  ## Generate swagger documentation
	FS_URL=/tmp flask -e test.env generate-api-schema > docs/api/open_api.json

generate-doc: generate-swagger ## Generate mkdocs documentation
	mkdocs build --strict

serve-doc: generate-swagger ## Serve mkdocs documentation
	mkdocs serve

help: ## Print this help message
	@grep -E '^[a-zA-Z_-]+:.*## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

i18n-code2pot:
	pybabel extract -F babel.cfg -o geovisio/translations/messages.pot geovisio/
	msginit --locale=en --no-translator --input=geovisio/translations/messages.pot --output=geovisio/translations/en/LC_MESSAGES/messages.po

i18n-po2code:
	pybabel compile -d geovisio/translations/

build-docker:
	docker buildx build \
		--build-arg GIT_DESCRIBE=`git describe` \
		--label=org.opencontainers.image.created=`date -u +'%Y-%m-%dT%H:%M:%SZ'` \
		--label=org.opencontainers.image.version=`cat geovisio/__init__.py | grep -e '^__version__' | cut -d \" -f 2` \
		-t panoramax/api:develop .