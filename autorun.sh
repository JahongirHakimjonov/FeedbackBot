#!/bin/bash

# Proyektni o'chirish
docker-compose down

# Proyektni ishga tushirish
docker-compose up -d  --build
