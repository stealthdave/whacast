FROM python:3.9

COPY ./src /app
WORKDIR /app
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

CMD python -u -m whacast settings.json
