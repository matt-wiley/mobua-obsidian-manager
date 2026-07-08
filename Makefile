.PHONY: build docker dev clean release

release:
	@test -n "$(VERSION)" || { echo "Usage: make release VERSION=x.y.z"; exit 1; }
	@echo "$(VERSION)" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+([-.].*)?$$' \
		|| { echo "VERSION must be semver, e.g. 0.2.0"; exit 1; }
	git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@echo "Created annotated tag v$(VERSION). Push it with:"
	@echo "  git push origin v$(VERSION)"

build:
	cd frontend && npm run build
	rm -rf backend/obsidian_manager/static/*
	cp -r frontend/build/* backend/obsidian_manager/static/
	cd backend && uv build

docker: build
	docker build \
		--build-arg BUILD_VERSION=$(shell git describe --tags --dirty) \
		--build-arg BUILD_COMMIT=$(shell git rev-parse --short HEAD) \
		--build-arg BUILD_DATE=$(shell date -u +%Y-%m-%dT%H:%M:%SZ) \
		-t obsidian-manager:$(shell git describe --tags --dirty) \
		-t obsidian-manager:latest \
		.

dev:
	@echo "Start both processes:"
	@echo "  Terminal 1: cd backend && uv run uvicorn obsidian_manager.main:app --reload"
	@echo "  Terminal 2: cd frontend && npm run dev"

clean:
	rm -rf backend/obsidian_manager/static/*
	rm -rf backend/dist/
	rm -rf frontend/.svelte-kit/
