FROM node:22-bookworm-slim AS frontend-build

WORKDIR /frontend

COPY OneRoster-Frontend/package.json OneRoster-Frontend/package-lock.json ./
RUN npm ci

COPY OneRoster-Frontend/ ./
RUN npm run build


FROM python:3.13.2-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY . /app
COPY --from=frontend-build /frontend/dist /app/OneRoster-Frontend/dist

EXPOSE 3000

CMD ["sh", "/app/start.sh"]
