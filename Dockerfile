# Expects a pre-built wheel in backend/dist/ — run `make build` first.
FROM python:3.12-slim
WORKDIR /app

COPY backend/dist/*.whl ./
RUN pip install --no-cache-dir *.whl && rm *.whl

ENV PORT=8000
ENV DB_PATH=/data/obsidian.db
ENV DATA_DIR=/data

EXPOSE 8000
VOLUME ["/vault", "/data"]
CMD ["obsidian-manager"]
