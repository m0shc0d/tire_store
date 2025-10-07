FROM python:3.12-slim

WORKDIR /app

RUN pip install hatch

COPY . .

ENV HATCH_ENV_TYPE=virtual
ENV HATCH_ENV_DIR=/app/.hatch

RUN hatch env create dev

ENV VIRTUAL_ENV=/app/.hatch/dev
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

CMD ["hatch", "run", "dev:prestart"]
CMD ["hatch", "run", "dev:server"]
