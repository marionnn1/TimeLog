# Congelamos en bullseye (Debian 11) para compatibilidad total con el driver de Microsoft
FROM python:3.10-slim-bullseye

# 1. Instalamos las dependencias del sistema y el Driver ODBC 17 de SQL Server
RUN apt-get update && apt-get install -y \
    curl apt-transport-https gnupg2 unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && apt-get clean -y

# 2. Establecemos el directorio de trabajo
WORKDIR /app

# 3. Copiamos los requisitos y los instalamos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Exponemos el puerto
EXPOSE 5000

# 5. Comando para arrancar Flask
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]