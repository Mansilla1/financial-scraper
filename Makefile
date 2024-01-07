.DEFAULT_GOAL := help

.PHONY: help
help:
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: up
up: ## up and drop you into a running container
	@echo "Running project"
	@docker-compose up -d && docker-compose exec api /bin/bash

.PHONY: rebuild
rebuild: ## rebuild Docker container
	@docker-compose up -d --build && docker-compose exec api /bin/bash

.PHONY: rebuild-bash
rebuild-bash: ## rebuild Docker container and up in sh
	@docker-compose up -d --build && docker-compose exec api /bin/bash

.PHONY: stop
stop: ## stop Docker container without removing them
	@docker-compose stop

.PHONY: down
down: ## down Docker container without removing them
	@docker-compose down
