

#!/bin/bash

# Verifica si se proporcionó el nombre de la app
if [ -z "$1" ]; then
  echo "Uso: $0 nombre_app"
  exit 1
fi

APP_NAME=$1

# Ejecutar el comando para crear la app de Django
python manage.py startapp $APP_NAME

# Crear subdirectorios personalizados dentro de la app
mkdir -p $APP_NAME/serializers
mkdir -p $APP_NAME/services
mkdir -p $APP_NAME/urls_$APP_NAME
mkdir -p $APP_NAME/utils
mkdir -p $APP_NAME/views_$APP_NAME

# Crear archivos __init__.py para convertir carpetas en paquetes Python
touch $APP_NAME/serializers/__init__.py
touch $APP_NAME/services/__init__.py
touch $APP_NAME/urls_$APP_NAME/__init__.py
touch $APP_NAME/utils/__init__.py
touch $APP_NAME/views_$APP_NAME/__init__.py

echo "App '$APP_NAME' creada con estructura personalizada."