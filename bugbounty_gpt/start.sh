#!/bin/bash

# Run the migration script
python -m bugbounty_gpt.db.migrate

# Start the main application
python -m bugbounty_gpt
