VERSION = 0.2.1

PACKAGE = nginx_statsd_sidecar

DOCKER_REGISTRY = caltechads

.PHONY: check-branch check-clean _release
.PHONY: FORCE

#======================================================================

clean:
	rm -rf *.tar.gz dist *.egg-info *.rpm
	find . -name "*.pyc" -exec rm '{}' ';'

dist: clean
	@uv build --sdist --wheel


# Allow overriding the main branch (defaults to master)
MAIN_BRANCH ?= master

# Gate checks
check-branch:
	@branch=$$(git rev-parse --abbrev-ref HEAD); \
	test "$$branch" = "$(MAIN_BRANCH)" || { \
	  echo "You're not on $(MAIN_BRANCH); aborting."; exit 1; }

check-clean:
	@test -z "$$(git status --untracked-files=no --porcelain)" || { \
	  echo "You have uncommitted changes; aborting."; exit 1; }

# Shared release recipe. Expects BUMP=dev|patch|minor|major
_release: compile check-branch check-clean
	@echo "Releasing $(BUMP) version"
	@bumpversion $(BUMP)
	@bin/release.sh

# Generate "release-<type>" targets that pass BUMP through
release-%:
	@case "$*" in dev|patch|minor|major) ;; \
	  *) echo "Invalid release type: $*"; exit 1;; esac
	@$(MAKE) _release BUMP=$*

compile: uv.lock
	@uv pip compile --group=docs pyproject.toml -o requirements.txt
	@git add requirements.txt
	# Commit may be a no-op if nothing changed; don't fail the release on that
	@git commit -m "DEV: Updated requirements.txt" || true

build:
	docker buildx build --platform linux/amd64,linux/arm64 -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest
	docker image prune -f

force-build: aws-login
	docker build --no-cache -t ${PACKAGE}:${VERSION} .
	docker tag ${PACKAGE}:${VERSION} ${PACKAGE}:latest

tag:
	docker tag ${PACKAGE}:${VERSION} ${DOCKER_REGISTRY}/${PACKAGE}:${VERSION}
	docker tag ${PACKAGE}:latest ${DOCKER_REGISTRY}/${PACKAGE}:latest

push: tag
	docker push ${DOCKER_REGISTRY}/${PACKAGE}

pull:
	docker pull ${DOCKER_REGISTRY}/${PACKAGE}:${VERSION}

scout:
	docker scout cves --only-severity=critical,high ${PACKAGE}:${VERSION}

dev:
	docker compose up

dev-detached:
	docker compose up -d

devdown:
	docker compose down

restart:
	docker compose restart nginx_statsd_sidecar

exec:
	docker exec -it nginx_statsd_sidecar /bin/bash

log:
	docker compose logs -f nginx_statsd_sidecar

logall:
	docker compose logs -f

docker-clean:
	docker stop $(shell docker ps -a -q)
	docker rm $(shell docker ps -a -q)

docker-destroy: docker-clean docker-destroy-db
	docker rmi -f $(shell docker images -q | uniq)
	docker image prune -f; docker volume prune -f; docker container prune -f
