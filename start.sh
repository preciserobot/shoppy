#!/bin/bash
service redis-server start
uvicorn app.main:app --host 0.0.0.0 --port 8000
