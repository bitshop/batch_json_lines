FROM python:3.12

COPY . /src/
WORKDIR /src
RUN pip install -r requirements.txt

CMD ["/usr/local/bin/python", "app.py"]

