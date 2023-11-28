FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install poetry
RUN poetry install

ENTRYPOINT ["poetry", "run", "finb"]
EXPOSE 16888
