#!/bin/bash
npm install
apt-get update && apt-get install -y libnss3 libatk1.0-0 libx11-xcb1 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libasound2
npm start