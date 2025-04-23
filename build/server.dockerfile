FROM debian:latest

RUN apt-get update; \
    apt-get install -y curl git; \
    curl -LsSf https://astral.sh/uv/install.sh | sh

RUN git -c advice.detachedHead=false clone --depth 1 --branch v0.4.2 https://github.com/maddinkunze/handcode; \
    cd handcode; \
    ~/.local/bin/uv sync

WORKDIR /handcode/src

CMD ["~/.local/bin/uv", "run", "server.py"]