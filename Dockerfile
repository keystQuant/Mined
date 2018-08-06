FROM python:3.6

RUN apt-get update && \
    apt-get install -y && \
    pip3 install uwsgi

COPY . /app

RUN pip3 install --upgrade pip && \
    pip3 install -q Django==1.11 && \
    pip3 install -r /app/requirements.txt

WORKDIR /app

RUN python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["uwsgi", "--ini", "/app/config/uwsgi.ini"]
