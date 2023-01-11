FROM python:3.10
ENV APP_HOME /app
WORKDIR $APP_HOME
ADD requirements_scrapy.txt .
RUN pip install -r requirements_scrapy.txt
ADD Input/ Input/
ADD creds/ creds/
ADD Clutter/ Clutter/
ADD scrapy.cfg .
ADD sheet_link.txt .
ADD runner.sh .
ADD main.py .
ENV FLASK_APP=main
ENV FLASK_ENV=development
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
