FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN python -m pip install --no-cache-dir --upgrade poetry
COPY pyproject.toml poetry.lock ./
RUN poetry export -f requirements.txt --without-hashes -o /app/requirements.txt
RUN pip install -r /app/requirements.txt

COPY . /app

COPY . /entrypoint.sh /

ENTRYPOINT ["sh", "entrypoint.sh"]

