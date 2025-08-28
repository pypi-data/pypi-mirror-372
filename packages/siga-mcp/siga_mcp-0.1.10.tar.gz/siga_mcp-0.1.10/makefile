.PHONY: run release

DEFAULT_GOAL := run

ifneq (,$(wildcard ./.env))
    include .env
    export
endif

run:
	uv run main.py

release:
	uv version --bump patch
	rm -rf dist
	uv build
	uv publish --token ${UV_PUBLISH_TOKEN}
