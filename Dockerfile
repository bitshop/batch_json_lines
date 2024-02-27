FROM python:3.12

COPY . /src/
WORKDIR /src
RUN pip install -r requirements.txt

EXPOSE 80/tcp
# CMD ["/usr/local/bin/python", "app.py"]
CMD ["gunicorn", "-b", "0.0.0.0:80", "app:app"]
