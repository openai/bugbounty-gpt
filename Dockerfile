# Use an official Python runtime as a parent image
FROM python:3.11-slim-bookworm

# Install Poetry
RUN pip install poetry

# Create a non-root user
RUN adduser --disabled-password --gecos '' myuser

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the local src directory contents, README.md, and the config file into the container
COPY bugbounty_gpt/ ./bugbounty_gpt/
COPY config.yaml .
COPY README.md .

# Copy only the pyproject.toml and poetry.lock files to install dependencies
COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy the Alembic configuration and migration scripts
COPY alembic.ini /usr/src/app/alembic.ini
COPY alembic /usr/src/app/alembic

# Change the owner of the Alembic directory to the non-root user
RUN chown -R myuser:myuser /usr/src/app/alembic
RUN mkdir -p /usr/src/app/alembic/versions && chown -R myuser:myuser /usr/src/app/alembic/versions

# Switch to the non-root user
USER myuser

# Accept EPHEMERAL_DB as a build argument
ARG EPHEMERAL_DB=false
ENV EPHEMERAL_DB=${EPHEMERAL_DB}

# If EPHEMERAL_DB is "true", run start.sh, otherwise run python -m src.main
CMD if [ "$EPHEMERAL_DB" = "true" ]; then /usr/src/app/bugbounty_gpt/start.sh; else python -m bugbounty_gpt; fi

