#!/usr/bin/env bash

uvicorn --port 8969 --host 0.0.0.0 siga_mcp.main:mcp --workers 2
