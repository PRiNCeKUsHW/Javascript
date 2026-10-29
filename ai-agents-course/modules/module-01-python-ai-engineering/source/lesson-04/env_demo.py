# env_demo.py: read configuration and secrets from environment variables
import os

api_key = os.environ.get("DEMO_API_KEY")
model = os.environ.get("DEMO_MODEL", "model-small")    # default if not set

if api_key is None:
    print("DEMO_API_KEY is not set: refusing to call the API")
else:
    print(f"key loaded ({len(api_key)} characters); never print the key itself")
print("model:", model)
