import tomllib
from os import getenv
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Load metadata from pyproject.toml
with open("pyproject.toml", "rb") as f:
    toml_object: dict[str] = tomllib.load(f).get("project", {})
    name = toml_object.get("name")
    description = toml_object.get("description")
    version = toml_object.get("version")

# Define config model using Pydantic
class ConfigClass(BaseModel):
    app_name: str
    description: str
    version: str
    api_key: Optional[str]

    hubspot_client_id: str
    hubspot_client_secret: str
    hubspot_redirect_uri: str
    groq_api_key: str
    model_name: str
    hubspot_base_url: str
    api_base_url: str
    email_smtp_server: str
    email_smtp_port: int
    email_username: str
    email_password: str
    mongo_uri:str
    mongo_db:str

# Create a config object using values from toml and .env
CONFIG = ConfigClass(
    app_name=name,
    description=description,
    version=version,
    api_key=getenv("GROQ_API_KEY"),

    hubspot_client_id=getenv("HUBSPOT_CLIENT_ID"),
    hubspot_client_secret=getenv("HUBSPOT_CLIENT_SECRET"),
    hubspot_redirect_uri=getenv("HUBSPOT_REDIRECT_URI"),
    groq_api_key=getenv("GROQ_API_KEY"),
    model_name=getenv("MODEL_NAME"),
    hubspot_base_url=getenv("HUBSPOT_BASE_URL"),
    api_base_url=getenv("API_BASE_URL"),
    email_smtp_server=getenv("EMAIL_SMTP_SERVER"),
    email_smtp_port=int(getenv("EMAIL_SMTP_PORT")),  # Must convert port to int
    email_username=getenv("EMAIL_USERNAME"),
    email_password=getenv("EMAIL_PASSWORD"),
    mongo_uri=getenv("MONGO_URI"),
    mongo_db=getenv("MONGO_DB")
)
