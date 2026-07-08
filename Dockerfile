# Expects a pre-built wheel in backend/dist/ — run `make build` first.
FROM python:3.12-slim
WORKDIR /app

COPY backend/dist/*.whl ./
RUN pip install --no-cache-dir *.whl && rm *.whl

ARG BUILD_VERSION=0+unknown
ARG BUILD_COMMIT=unknown
ARG BUILD_DATE=
ENV BUILD_VERSION=$BUILD_VERSION
ENV BUILD_COMMIT=$BUILD_COMMIT
ENV BUILD_DATE=$BUILD_DATE

ENV PORT=8000
ENV DB_PATH=/data/obsidian.db
ENV DATA_DIR=/data

EXPOSE 8000
VOLUME ["/vault", "/data"]
CMD ["obsidian-manager"]
