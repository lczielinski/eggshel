FROM rust:1-slim AS builder
RUN cargo install egglog

FROM python:3.13-slim
COPY --from=builder /usr/local/cargo/bin/egglog /usr/local/bin/egglog
RUN apt-get update && apt-get install -y --no-install-recommends make && rm -rf /var/lib/apt/lists/*

WORKDIR /eggshel
COPY . .

CMD ["bash"]
