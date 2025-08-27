
import json
import os
import sys
from typing import Callable, Optional, TypeVar
from box import box_from_file
import boto3

T = TypeVar('T')


def load_config(file_path: str, aws_session: Optional[boto3.Session] = None) -> T:
    _, fileext = os.path.splitext(file_path)
    box = None

    if fileext in ['.yaml', '.yml']:
        box = box_from_file(file_path, 'yaml')
    elif fileext == '.json':
        box = box_from_file(file_path, 'json')

    if not box:
        raise Exception(f'Config file must be .yml, .yaml, or .json')

    _resolve_all_uris(box, aws_session)

    return box


def _resolve_all_uris(data: T, aws_session: Optional[boto3.Session]) -> None:
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                _resolve_all_uris(value, aws_session)
            elif isinstance(value, str):
                try:
                    data[key] = _resolve_uri(value, aws_session)
                except Exception as e:
                    print(f"Failed to resolve URI '{value}': {str(e)}", file=sys.stderr)
                    raise
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                _resolve_all_uris(item, aws_session)
            elif isinstance(item, str):
                try:
                    data[i] = _resolve_uri(item, aws_session)
                except Exception as e:
                    print(f"Failed to resolve URI '{item}': {str(e)}", file=sys.stderr)
                    raise


def _transform_data(data: T, transformation: Callable[[T, Optional[boto3.Session]], T], aws_session: Optional[boto3.Session]) -> T:
    if isinstance(data, dict):
        return {key: _transform_data(value, transformation, aws_session) for key, value in data.items()}
    elif isinstance(data, list):
        return [_transform_data(item, transformation, aws_session) for item in data]
    else:
        return transformation(data, aws_session)


def _resolve_ssm(parameter_name: str, aws_session: Optional[boto3.Session] = None) -> str:

    # All SSM params start with '/' whether we want them to or not
    if not parameter_name.startswith('/'):
        parameter_name = '/' + parameter_name

    # Initialize an AWS SSM client using the provided session or the default session
    ssm_client = aws_session.client('ssm') if aws_session else boto3.client('ssm')

    # Retrieve the parameter value from AWS SSM
    response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)

    # Extract the parameter value from the response
    parameter_value = response['Parameter']['Value']

    return parameter_value


def _resolve_secret(secret_name: str, aws_session: Optional[boto3.Session] = None) -> str:

    # Initialize an AWS Secrets Manager client using the provided session or the default session
    secrets_manager_client = aws_session.client('secretsmanager') if aws_session else boto3.client('secretsmanager')

    # Retrieve the secret value from AWS Secrets Manager
    response = secrets_manager_client.get_secret_value(SecretId=secret_name)

    # Extract the secret value from the response
    secret_value = response['SecretString']

    return secret_value


def _resolve_s3(bucket_key: str, aws_session: Optional[boto3.Session] = None) -> str:
    try:
        # Initialize an AWS S3 client using the provided session or the default session
        s3_client = aws_session.client('s3') if aws_session else boto3.client('s3')

        # Extract bucket and key from bucket_key
        bucket, key = bucket_key.split("/", 1)

        # Retrieve the object from AWS S3
        response = s3_client.get_object(Bucket=bucket, Key=key)

        # Read the object's content and decode it
        content = response['Body'].read().decode('utf-8')

        return content
    except Exception as e:
        raise Exception(f"Failed to resolve S3 bucket/key '{bucket_key}' due to: {str(e)}") from e


def _resolve_file(file_path: str) -> str:
    try:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
    except Exception as e:
        raise Exception(f"Failed to resolve file at '{file_path}' due to: {str(e)}") from e


def _resolve_uri(uri: str, aws_session: Optional[boto3.Session] = None) -> str:
    try:
        if uri.startswith('secret://'):
            secret_name = uri[9:]
            return _resolve_secret(secret_name, aws_session)
        elif uri.startswith('ssm://'):
            parameter_name = uri[6:]
            return _resolve_ssm(parameter_name, aws_session)
        elif uri.startswith('s3://'):
            bucket_key = uri[5:]
            return _resolve_s3(bucket_key, aws_session)
        elif uri.startswith('env://'):
            env_var_name = uri[6:]
            return os.environ.get(env_var_name, '')
        elif uri.startswith('json+env://'):
            env_var_name = uri[11:]
            json_value = os.environ.get(env_var_name, '')
            return json.loads(json_value)
        elif uri.startswith('json+secret://'):
            secret_name = uri[14:]
            secret_value = _resolve_secret(secret_name, aws_session)
            return json.loads(secret_value)
        elif uri.startswith('json+ssm://'):
            ssm_param_name = uri[11:]
            ssm_param_value = _resolve_ssm(ssm_param_name, aws_session)
            return json.loads(ssm_param_value)
        elif uri.startswith('json+s3://'):
            bucket_key = uri[10:]
            s3_content = _resolve_s3(bucket_key, aws_session)
            return json.loads(s3_content)
        elif uri.startswith('file://'):
            file_path = uri[7:]
            return _resolve_file(file_path)
        elif uri.startswith('json+file://'):
            file_path = uri[12:]
            file_content = _resolve_file(file_path)
            return json.loads(file_content)
        else:
            return uri
            
    except Exception as original_error:
        raise Exception(f"Failed to resolve URI '{uri}' due to: {str(original_error)}") from original_error

