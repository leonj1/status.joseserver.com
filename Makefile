# Declare phony targets (targets that don't represent files)
.PHONY: test

# Run tests in Docker
test:
	docker build -f Dockerfile.test -t status-service-tests .
	docker run --rm status-service-tests