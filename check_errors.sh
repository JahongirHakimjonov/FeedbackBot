#!/bin/bash

# Konteyner nomlari
BOT_CONTAINER_NAME="feedbackbotapp_bot_1"
SUPPORT_BOT_CONTAINER_NAME="feedbackbotapp_support_bot_1"
WEB_CONTAINER_NAME="feedbackbotapp_web_1"
POSTGRES_CONTAINER_NAME="postgres_db"

# Log fayllarni tekshirish va xatolikni topish
BOT_ERROR_LOG=$(docker logs $BOT_CONTAINER_NAME 2>&1 | grep "ERROR")
SUPPORT_BOT_ERROR_LOG=$(docker logs $SUPPORT_BOT_CONTAINER_NAME 2>&1 | grep "ERROR")
WEB_ERROR_LOG=$(docker logs $WEB_CONTAINER_NAME 2>&1 | grep "ERROR")
POSTGRES_ERROR_LOG=$(docker logs $POSTGRES_CONTAINER_NAME 2>&1 | grep "ERROR")

# Bot konteyneri uchun xatolik tekshirish
if [ -n "$BOT_ERROR_LOG" ]; then
    echo "Bot konteynerida xatolik topildi: $BOT_ERROR_LOG"
    echo "Bot konteyneri qayta ishga tushirilmoqda..."
    docker-compose restart $BOT_CONTAINER_NAME
    echo "Bot konteyneri qayta ishga tushirildi."
else
    echo "Bot konteynerida xatolik topilmadi."
fi

# Support bot konteyneri uchun xatolik tekshirish
if [ -n "$SUPPORT_BOT_ERROR_LOG" ]; then
    echo "Support bot konteynerida xatolik topildi: $SUPPORT_BOT_ERROR_LOG"
    echo "Support bot konteyneri qayta ishga tushirilmoqda..."
    docker-compose restart $SUPPORT_BOT_CONTAINER_NAME
    echo "Support bot konteyneri qayta ishga tushirildi."
else
    echo "Support bot konteynerida xatolik topilmadi."
fi

# Web konteyneri uchun xatolik tekshirish
if [ -n "$WEB_ERROR_LOG" ]; then
    echo "Web konteynerida xatolik topildi: $WEB_ERROR_LOG"
    echo "Web konteyneri qayta ishga tushirilmoqda..."
    docker-compose restart $WEB_CONTAINER_NAME
    echo "Web konteyneri qayta ishga tushirildi."
else
    echo "Web konteynerida xatolik topilmadi."
fi

# Postgres konteyneri uchun xatolik tekshirish
if [ -n "$POSTGRES_ERROR_LOG" ]; then
    echo "Postgres konteynerida xatolik topildi: $POSTGRES_ERROR_LOG"
    echo "Postgres konteyneri qayta ishga tushirilmoqda..."
    docker-compose restart $POSTGRES_CONTAINER_NAME
    echo "Postgres konteyneri qayta ishga tushirildi."
else
    echo "Postgres konteynerida xatolik topilmadi."
fi
