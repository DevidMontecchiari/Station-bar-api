FROM python:3.14-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# Include the tools used to check the exercises.
COPY solution/requirements.txt solution/requirements-test.txt /tmp/dependencies/
RUN python -m pip install --no-cache-dir -r /tmp/dependencies/requirements-test.txt \
    && useradd --create-home --uid 10001 learner \
    && mkdir -p /data \
    && chown learner:learner /data
COPY --chown=learner:learner run.py check.py pyproject.toml ./
COPY --chown=learner:learner solution/ ./solution/
COPY --chown=learner:learner starter/ ./starter/
COPY --chown=learner:learner checks/ ./checks/
USER learner
EXPOSE 8000
CMD ["python", "run.py", "solution", "--host", "0.0.0.0"]

# Git is available for the learner development workflow in Codespaces.
FROM runtime AS codespace
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends git openssh-client ca-certificates \
    && rm -rf /var/lib/apt/lists/*
USER learner
