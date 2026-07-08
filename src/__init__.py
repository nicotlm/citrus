from dotenv import load_dotenv
import logging

load_dotenv()


# Logging
logger = logging.getLogger("citrus")
logger.setLevel(logging.INFO)

# Create handlers
file_handler = logging.FileHandler("log/citrus.log")
console_handler = logging.StreamHandler()

# Set level and format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)