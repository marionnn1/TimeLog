import os
from urllib.parse import quote_plus
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

KV_URL = os.getenv("AZURE_KEYVAULT_URL")
credential = DefaultAzureCredential()
client = SecretClient(vault_url=KV_URL, credential=credential)

def get_secret_from_key_vault(secret_name):
    try:
        return client.get_secret(secret_name).value
    except Exception as e:
        print(f"Error retrieving secret {secret_name} from Key Vault: {e}")
        return None


server = get_secret_from_key_vault("DB-SERVER")
database = get_secret_from_key_vault("DB-NAME")
username = get_secret_from_key_vault("DB-USER")
password = get_secret_from_key_vault("DB-PASSWORD")
port = "1433"
driver = "ODBC Driver 17 for SQL Server"

pwd_encoded = password
driver_encoded = driver

SQLALCHEMY_DATABASE_URI = (
    f"mssql+pyodbc://{username}:{pwd_encoded}@{server}:{port}/{database}"
    f"?driver={driver_encoded}&Encrypt=yes&TrustServerCertificate=yes&Connection+Timeout=30"
)