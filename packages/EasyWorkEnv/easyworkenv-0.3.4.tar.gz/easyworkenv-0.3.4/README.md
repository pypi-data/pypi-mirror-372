# EasyWorkEnv

This is a Python package that simplifies the management of environment variables.

## Compatibility
### Supported environment file formats
- `.json`
- `.env`
- `.yaml`

## Example usage

```python
from EasyWorkEnv import Config

# Creation of the object containing all your environment variables

config = Config(".env")

# Variables retrieved from the environment

my_env = config.ENV
my_api_key = config.API_KEY

# Nested information

my_bdd_host = config.BDD.Host
my_bdd_database_name = config.BDD.DATABASE_NAME
```
