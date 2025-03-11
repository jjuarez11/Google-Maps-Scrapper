#!/bin/bash
playwright install chromium
gunicorn -t 3600 -b 0.0.0.0:10000 app:app
