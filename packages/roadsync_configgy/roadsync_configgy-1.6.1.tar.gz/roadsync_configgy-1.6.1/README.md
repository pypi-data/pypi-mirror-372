# Configgy
Configgy help you keep configuration files isomorphic.
You can keep your configs entirely in your repo, loading secret values externally.
Configs can be yaml or json, and can pull values from SSM, Secrets Manager, or S3.
Fetched values can be strings or JSON.

> **Note**: As a design decision, Configgy will never support default values or cascading/inherited configs. All configs should be straightforward to read and not increase cognitive load. This library is designed to fail fast and raise an exception, not continue with bad data.

# Installation
```sh
pip install roadsync_configgy
```
or
```sh
poetry add roadsync_configgy
```

# Example Use
Assuming:
```
project/
├── configs/
│   ├── local.yaml
│   └── deployed.yaml
└── main.py
```
```yaml
# local.yaml
port: 3001
env: 'local'
api_key: 'fakeabc123'
users_table: 'AppName-Users'
documents_table: 'AppName-Documents'
service_host: 'locahost'
```
```yaml
# deployed.yaml
port: 3001
env: 'ssm://env'    # dev|test|prod
api_key: 'secret://myservice/api_key'
users_table: 'AppName-Users'
documents_table: 'AppName-Documents'
service_host: 'ssm://myservice/host' # api.myservice.com
```
```python
import os
from roadsync_configgy import load_config
from dataclasses import dataclass

@dataclass
class AppConfig:
    port: int
    env: str
    api_key: str
    users_table: str
    documents_table: str
    service_host: str

# Determine which environment we're running in
config_name = os.getenv('CONFIG')

# Load from path/to/config.yaml
config: AppConfig = load_config(f'configs/{config_name}.yaml')

http_serve(config.port)
```
```sh
# example usage
CONFIG='local' flask run
```

## Supported Loading Types
```
secret://my-secret-key
ssm://my-ssm-parameter
s3://my-s3-bucket/my-file.txt
env://MY_ENV_VARIABLE

# parses the json
json+secret://my-secret-key
json+ssm://my-ssm-parameter
json+s3://my-s3-bucket/my-json-file.json
json+env://MY_ENV_VARIABLE
```

example config, showcasing all the loading types
```yaml

# path/to/config.yaml

# Database settings using AWS Secrets Manager
db:
  host: 'db.services.local'
  username: "secret://db-username"  # Fetches username from Secrets Manager
  password: "secret://db-password"  # Fetches password from Secrets Manager

# AWS settings using AWS SSM
aws:
  region: "ssm://aws-region"            # Fetches AWS region from SSM
  instance_id: "ssm://aws-instance-id"  # Fetches AWS instance ID from SSM

# Application settings using Environment Variables
app:
  mode: "env://APP_MODE"  # Fetches app mode from environment variable APP_MODE
  port: "env://APP_PORT"  # Fetches app port from environment variable APP_PORT

# Feature toggles using JSON in Environment Variables
features:
  enabled: "json+env://ENABLED_FEATURES"  # Fetches JSON array from env var ENABLED_FEATURES

# Secrets in JSON format from AWS Secrets Manager
secrets:
  api_keys: "json+secret://api-keys"  # Fetches and parses JSON API keys from Secrets Manager

# AWS S3 files
files:
  config_file: "s3://my-bucket/config-file"  # Fetches config file from S3 bucket

# Data in JSON format from AWS S3
s3_data:
  important_data: "json+s3://my-bucket/important-data.json"  # Fetches and parses JSON from S3

```
