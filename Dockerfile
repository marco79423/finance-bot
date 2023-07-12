FROM python:3.10

WORKDIR /app

COPY . .

RUN pip install -e .

ENTRYPOINT ["finb"]
CMD ["serve"]
EXPOSE 8888