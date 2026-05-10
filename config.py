import os
from dotenv import load_dotenv

load_dotenv()

AIRLABS_API_KEY = os.getenv("AIRLABS_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
