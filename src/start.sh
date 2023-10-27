#!/bin/bash

# Run the migration script
python -m src.db.migrate

# Start the main application
python -m src.main
