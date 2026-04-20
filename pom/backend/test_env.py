import os
from dotenv import load_dotenv, find_dotenv

env_file = find_dotenv()
print(f"Loading .env from: {env_file}")
load_dotenv(override=True)

print(f"MAIL_SERVER = {os.getenv('MAIL_SERVER')}")
print(f"MAIL_PORT = {os.getenv('MAIL_PORT')}")

# Also check if .env file has the right value
with open('.env', 'r') as f:
    for line in f:
        if 'MAIL_SERVER' in line:
            print(f"In .env file: {line.strip()}")
