import argparse
import sys
import json
import boto3
from ruamel.yaml import YAML
from .config import load_config

def main():
    parser = argparse.ArgumentParser(
        description="Configgy CLI for materializing configuration files."
    )
    parser.add_argument(
        "command", choices=["materialize"], help="The command to execute."
    )
    parser.add_argument(
        "source", help="The path to the source configuration file."
    )
    parser.add_argument(
        "destination", help="The path where the materialized configuration will be saved."
    )
    parser.add_argument(
        "--aws-profile", help="The AWS profile to use for credential resolution.", default=None
    )

    args = parser.parse_args()

    # Initialize AWS session if profile is provided
    aws_session = boto3.Session(profile_name=args.aws_profile) if args.aws_profile else None

    # Infer file type and validate
    _, file_ext = args.source.lower().rsplit('.', 1)

    match file_ext:
        case "json":
            file_type = "json"
        case "yaml" | "yml":
            file_type = "yaml"
        case _:
            print(f"Error: Unsupported file type '{file_ext}'. Must be json, yaml, or yml.", file=sys.stderr)
            sys.exit(1)

    try:
        # Load configuration using the specified file type and AWS session
        config = load_config(args.source, aws_session)

        with open(args.destination, "w") as dest_file:
            match file_type:
                case "json":
                    json.dump(config.to_dict(), dest_file, indent=2)
                case "yaml":
                    yaml = YAML()
                    yaml.dump(config.to_dict(), dest_file)

        print(f"Materialized config written to {args.destination}")
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
