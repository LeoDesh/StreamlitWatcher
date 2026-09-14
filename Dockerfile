# --- Stage 1: Build-Umgebung (Nutzt das schnelle uv) ---
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

# Arbeitsverzeichnis & uv-Optimierungen setzen
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
WORKDIR /app

# Nur Projektspezifikationen kopieren, um Caching optimal zu nutzen
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# --- Stage 2: Minimales finales Image ---
FROM python:3.13-slim

WORKDIR /app

# Nur die fertige virtuelle Umgebung aus der ersten Stage kopieren
COPY --from=builder /app/.venv /app/.venv

# Restlichen Anwendungscode kopieren
COPY . .

# Den Pfad zur virtuellen Umgebung standardmäßig nutzen
ENV PATH="/app/.venv/bin:$PATH"

# Port freigeben und Anwendung starten
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.fileWatcherType=poll"]
