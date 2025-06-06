FROM python:3.13.1
LABEL authors="pavsri"
WORKDIR /app

COPY requirements.txt .

RUN apt-get update \
    && apt-get install -y libsasl2-dev libldap2-dev libssl-dev  \
    && python -m pip wheel --wheel-dir=/tmp python-ldap==3.4.4

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

ENV PYTHONUNBUFFERED=1

CMD ["/usr/local/bin/python", "manage.py", "runserver", "0.0.0.0:8080"]
