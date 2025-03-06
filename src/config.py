import os
from dotenv import load_dotenv, find_dotenv

# Load environment variables
_ = load_dotenv(find_dotenv())

# Canvas API Configuration
CANVAS_BASE_URL = "https://uc.instructure.com/api/v1"
DEFAULT_PARAMS = {
    "per_page": 100
}

# OpenAI Configuration
DEFAULT_MODEL = "gpt-4o"
DEFAULT_TEMPERATURE = 0.5

# Grading Configuration
DEFAULT_POST_POINTS = 20
DEFAULT_REPLY_POINTS = 7.5

# Output Directory
OUTPUT_DIR = "Canvas_Discussion_Exports"