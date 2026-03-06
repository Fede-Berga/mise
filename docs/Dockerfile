FROM python:3.12-alpine AS builder

WORKDIR /build

COPY docs/requirements.txt /build/requirements.txt
RUN pip install --no-cache-dir -r /build/requirements.txt

COPY mkdocs.yml /build/mkdocs.yml
COPY docs /build/docs

RUN mkdocs build --strict --site-dir /build/site

FROM nginx:1.27-alpine AS runtime

COPY --from=builder /build/site /usr/share/nginx/html

EXPOSE 80
