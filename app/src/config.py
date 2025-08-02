import os

# --- Configuration ---
# Loaded from environment variables for flexibility in AWS Lambda.
MEILI_URL = os.environ.get("MEILI_URL", "http://18.217.93.15:7700")
MEILI_MASTER_KEY = os.environ.get("MEILI_MASTER_KEY", "piszah-9Fuhde-pangaw")
# Default country is a two-letter country code.
DEFAULT_COUNTRY = os.environ.get("DEFAULT_COUNTRY", "us")
OUTPUT_FILE = os.environ.get("OUTPUT_FILE", "events.json")

SAVE_TO_MEILISEARCH = os.environ.get("SAVE_TO_MEILISEARCH", "false").lower() == "true" 