import os
import dotenv

# Load environment variables from .env file
dotenv.load_dotenv()


# Defines where the home directory is - can be overridden
HOME_DIR:str = os.getenv("RESOLVER_HOME", os.getcwd())


# Default runtime directory
RUNTIME_DIR:str = os.getenv("RESOLVER_RUNTIME_DIR", f"{HOME_DIR}/dependency-resolver-runtime")


# Default cache directory
CACHE_DIR:str = os.getenv("RESOLVER_CACHE_DIR", f"{RUNTIME_DIR}/.resolverCache")


# Default name of the cache - this can be defined per project in the json configuration file (e.g. dependency_resolver.json)
CACHE_DEFAULT_NAME:str = "default"


# Logging constants
LOG_DIR:str = os.getenv("RESOLVER_LOG_DIR", RUNTIME_DIR)
LOG_TO_FILE:str = f"{LOG_DIR}/resolver.log"
