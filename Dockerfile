FROM python:3.11.9-slim

WORKDIR /

COPY ./requirements.txt /requirements.txt

RUN pip install -r requirements.txt

COPY ./ /

CMD [ "fastapi", "run", "main.py", "--port", "80" ]