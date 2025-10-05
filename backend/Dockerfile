FROM python:3.12-slim

WORKDIR /app

RUN pip install hatch

COPY . .

RUN hatch env create dev

CMD ["hatch", "run", "dev:server"]
