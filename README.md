# BugCrowd GPT Classifier

This project is a system designed to manage, classify, and process BugCrowd submissions using OpenAI, and a Postgres Database for data storage. It provides an automatic handling mechanism for submissions and can be run directly or within a Docker container.

## Table of Contents

- [BugCrowd GPT Clasifier](#bugcrowd-gpt-clasifier)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Getting Started](#getting-started)
    - [Configuration](#configuration)
      - [`config.yaml` File](#configyaml-file)
        - [API Settings](#api-settings)
        - [User Settings](#user-settings)
        - [Categories](#categories)
        - [OpenAI Prompt](#openai-prompt)
      - [Environment Variables](#environment-variables)
      - [Docker Compose](#docker-compose)
  - [Environment Variables for Docker Compose](#environment-variables-for-docker-compose)

## Prerequisites

Before starting, make sure you have the following installed:

- Docker
- Docker Compose

## Getting Started
As it stands, there is a Dockerfile within the root directory of this repository that, upon being built, will download all depenedencies and will package everything up for usage. After configuring the application and setting all sensitive environment variables, you can run this Dockerfile and start classifying and triaging results immediately.

To actually test your configuration, it is reccomended that you take utilize docker-compose to quickly spin-up and clear-out an ephermal database. Connect locally to the database with `psql` and inspect classifications.

If Docker isn't your cup of tea, you can also install the requirements locally and run the classifier/responder via `python -m src.main`

### Configuration

Configuration of the application involves setting up the `config.yaml` file as well as certain environment variables. Below are detailed descriptions of each configuration option. The current `config.yaml` is a working example that you can base your changes off of.

#### `config.yaml` File

##### API Settings

- `base_url`: URL of the Bugcrowd API, e.g. `"https://api.bugcrowd.com"`.
- `openai_model`: Chat model used for the OpenAI integration, e.g. `"gpt-4"`.

##### User Settings

- `user_id`: Identifier for the user interacting with the application. This represents the Bugcrowd ID of the user assigned to the report, typically a Bugcrowd employee. This user is responsible for validating that the actual report is indeed correctly triaged. It can be left empty as `""` if not needed for a particular configuration.

- `filter_program`: Identifier for the specific Bugcrowd program that you're targeting. This configuration is used to filter API responses so that only the submissions from the program specified here are fetched. For example, it could be set to `"openai-test-sandbox"` to ensure that only submissions related to that particular program are retrieved and processed.


##### Categories

- `valid`: A list of all valid categories available for classifying reports. These categories encompass the entire range of possible classifications within the system. For example, they may include categories like "Functional Bugs or Glitches," "Customer Support Issues," "Security Report," etc. Every report submitted must be classified into one of these valid categories.

- `default`: Specifies the default category to be assigned when a submission fails to be classified into any of the `valid` categories. The value should be one of the categories listed under `valid`. Typically, this should be a category that doesn't have an automated response attached to it, so manual handling can be applied as needed. For example, it could be set to `"Security Report"` if this is a category that requires further manual review.

- `response`: Defines a subset of the `valid` categories that the system will close and respond to. It consists of a list of objects, each containing two keys: `name` and `response`. The `name` must match one of the valid category names, and `response` provides a corresponding template response for that category. These template responses will be used to automatically reply to submissions that are classified into these specific categories. For example, a response to "Functional Bugs or Glitches" might provide information on how to submit the report through standard support channels since it falls outside the scope of a security-focused bug bounty program.

##### OpenAI Prompt

- `openai_prompt`: A multi-line string that specifies the instructions, categories, and guidelines for classifying reports. The example in `config.yaml` is a great place to start building the prompt for your specific program.

#### Environment Variables

- `BUGCROWD_API_KEY`: API key for Bugcrowd, should be stored as an environment variable.
- `OPENAI_API_KEY`: API key for OpenAI, should be stored as an environment variable.
- `SQLALCHEMY_URL`: Connection URL for the database, utilizing an asynchronous driver such as `asyncpg`. This URL should follow the format `postgresql+asyncpg://<username>:<password>@<host>:<port>/<database>`, where you replace the placeholders with your specific PostgreSQL database connection details.

#### Docker Compose

The `docker-compose.yaml` file defines the containers for the application and database, including build arguments and volumes for data persistence. Specifically, it facilitates the process of testing changes to the configuration, especially those related to valid categories, which are translated into an Enum class and ingested as a type into the database.

When modifying category types, the associated Enum type needs to be reset — a change that alembic doesn't effectively detect. To quickly test such configuration changes, the `docker-compose` setup enables the use of an ephemeral database model, where the entire schema, including Enums and tables, can be discarded and rebuilt. The `ephemeral_db` argument in the Dockerfile controls whether to use this temporary database or point to a long-living production database.

By running `docker-compose up --build` and `docker-compose down -v`, you can repeatedly test changes to your config in a contained environment, ensuring that everything is functioning as expected without affecting the actual production setup.

In a production environment, manage alembic scripts manually and build the Dockerfile without the `ephemeral_db` argument, pointing to a long-living production database instead. This approach guarantees that the Docker Compose setup accurately reflects the structure and behavior of the production system while allowing for flexible and rapid testing during development.

1. **Configuration**: Make sure to properly set up the configuration in the `config.yaml` file, as well as required environment variables, before building and running the application. Detailed instructions are provided in the Configuration section below.

2. **Build the Docker Containers**: Navigate to the project directory and run the following command:

    ```bash
    docker-compose build
    ```

3. **Run the Containers**: Once the build is complete, start the containers with:

    ```bash
    docker-compose up
    ```

4. **Stop and Remove Containers**: To stop and remove everything, use:

    ```bash
    docker-compose down -v
    ```

   The `-v` option will also remove the volume used to persist the database data.

## Environment Variables for Docker Compose

When using Docker Compose to build and run containers for the purpose of testing configuration changes, you'll need to provide certain environment variables. These variables are specifically for the Docker Compose setup and can be set in the `docker-compose.yml` file:

- `DB_USER`: Database user, used for connecting to the ephemeral database in Docker Compose.
- `DB_PASSWORD`: Database password, used for connecting to the ephemeral database in Docker Compose.
- `DB_NAME`: Database name, used for specifying the database within the ephemeral database environment in Docker Compose.
- `BUGCROWD_API_KEY`: BugCrowd API key.
- `OPENAI_API_KEY`: OpenAI API key.
- ... and any other environment variables required for your specific testing configuration.

These environment variables are essential for defining the database connection and other parameters within the Docker Compose setup, enabling you to repeatedly test changes to your configuration without affecting general production workloads. They facilitate the process of rebuilding the schema, including Enums and tables, in a contained environment, and should be adjusted according to the needs of your specific test setup.
