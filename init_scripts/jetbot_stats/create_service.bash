#!/bin/bash

ABSOLUTE_PATH="$(pwd)"

# Имя службы: второй аргумент или значение по умолчанию
SERVICE_NAME="jetbot_telemetria"

# Имя файла службы (с расширением .service)
SERVICE_FILE="${SERVICE_NAME}.service"

# Генерируем содержимое файла службы
cat > "$SERVICE_FILE" <<EOF
[Service]
ExecStart=$ABSOLUTE_PATH/jetbot_stats.py
Restart=always
User=root
Group=root
StandardOutput=journal
StandardError=journal
EOF

echo "Файл службы создан: $SERVICE_FILE"