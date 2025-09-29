# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Устанавливаем hatch
RUN pip install hatch

# Копируем весь backend
COPY . .

# Устанавливаем зависимости через hatch
RUN hatch env create dev

# Запускаем сервер разработки
CMD ["hatch", "run", "dev:server"]
