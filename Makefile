.PHONY: build dev clean

build:
	cd frontend && npm run build
	rm -rf backend/obsidian_manager/static/*
	cp -r frontend/.svelte-kit/output/client/* backend/obsidian_manager/static/
	cd backend && uv build

dev:
	@echo "Start both processes:"
	@echo "  Terminal 1: cd backend && uv run uvicorn obsidian_manager.main:app --reload"
	@echo "  Terminal 2: cd frontend && npm run dev"

clean:
	rm -rf backend/obsidian_manager/static/*
	rm -rf backend/dist/
	rm -rf frontend/.svelte-kit/
