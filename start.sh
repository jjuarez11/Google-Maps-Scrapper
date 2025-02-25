#!/bin/bash
playwright install chromium
gunicorn -b 0.0.0.0:10000 app:app
