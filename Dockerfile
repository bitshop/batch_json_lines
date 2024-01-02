FROM python:3.12

COPY . /src/
WORKDIR /src
RUN pip install -r requirements.txt

EXPOSE 8000/tcp
CMD ["/usr/local/bin/python", "app.py"]
