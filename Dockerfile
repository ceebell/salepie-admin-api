FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# COPY requirements.txt /
# RUN pip3 install -r /requirements.txt

VOLUME [ "/thelogs" ]

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY ./app /app

WORKDIR /app


