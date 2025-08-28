# © Copyright 2023-2025 Hewlett Packard Enterprise Development LP
import argparse
import os
import textwrap
import urllib.parse
from argparse import Namespace
from typing import Any, Dict, List, Optional, no_type_check

import boto3
import botocore
from pydantic import StrictInt

import aiolirest
from aioli import cli
from aioli.cli import render
from aioli.common.api import authentication
from aioli.common.api.errors import NotFoundException
from aioli.common.declarative_argparse import Arg, Cmd, Group
from aiolirest.models.trained_model_registry import TrainedModelRegistry
from aiolirest.models.trained_model_registry_request import TrainedModelRegistryRequest

# Avoid reporting BrokenPipeError when piping `tabulate` output through
# a filter like `head`.
FLUSH = False


@authentication.required
@no_type_check
def list_registries(args: Namespace) -> None:
    def format_json(response: List[TrainedModelRegistry]) -> List[Dict[str, str]]:
        regs = []
        for r in response:
            # Don't use the r.to_json() method as it adds backslash escapes for double quote
            d = r.to_dict()
            d.pop("id")
            d.pop("modifiedAt")
            regs.append(d)

        return regs

    def format_deployment(
        response: List[TrainedModelRegistry], args: Namespace, projects_api: aiolirest.ProjectsApi
    ) -> None:
        def format_registry(e: TrainedModelRegistry) -> List[Any]:
            result = [
                e.project,
                e.name,
                e.type,
                e.access_key,
                e.bucket,
                e.secret_key,
                e.endpoint_url,
            ]
            return result

        headers = [
            "Project",
            "Name",
            "Type",
            "Access Key",
            "Bucket",
            "Secret Key",
            "Endpoint URL",
        ]

        values = [format_registry(r) for r in response]
        render.tabulate_or_csv(headers, values, args.csv)

    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)
        response = api_instance.registries_get()
        projects_instance = aiolirest.ProjectsApi(session)

    if args.json:
        render.print_json(format_json(response))
    elif args.yaml:
        print(render.format_object_as_yaml(format_json(response)))
    else:
        format_deployment(response, args, projects_instance)


@authentication.required
def create(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)

        r = TrainedModelRegistryRequest(
            name=args.name,
            accessKey=args.access_key,
            bucket=args.bucket,
            endpointUrl=args.endpoint_url,
            secretKey=args.secret_key,
            type=args.type,
            insecureHttps=args.insecure_https,
            project=args.project,
        )
        api_instance.registries_post(r)


def lookup_registry(name: str, api: aiolirest.RegistriesApi) -> TrainedModelRegistry:
    for r in api.registries_get():
        if r.name == name:
            return r
    raise NotFoundException(f"registry {name} not found")


def lookup_registry_by_id(
    ident: Optional[str], api: aiolirest.RegistriesApi
) -> TrainedModelRegistry:
    for r in api.registries_get():
        if r.id == ident:
            return r
    raise NotFoundException(f"registry with ID {ident} not found")


def lookup_registry_name_by_id(ident: Optional[str], api: aiolirest.RegistriesApi) -> Any:
    if not ident:
        return ""
    r = lookup_registry_by_id(ident, api)
    if r:
        return r.name
    raise NotFoundException(f"registry with ID {ident} not found")


@authentication.required
def show_registry(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)

    registry = lookup_registry(args.name, api_instance)

    d = registry.to_dict()
    if args.json:
        render.print_json(d)
    else:
        print(render.format_object_as_yaml(d))


@authentication.required
def update(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)
        found = lookup_registry(args.registryname, api_instance)
        request = TrainedModelRegistryRequest(
            accessKey=found.access_key,
            bucket=found.bucket,
            endpointUrl=found.endpoint_url,
            name=found.name,
            secretKey=found.secret_key,
            type=found.type,
            project=found.project,
            insecureHttps=found.insecure_https,
        )

        if args.name is not None:
            request.name = args.name

        if args.type is not None:
            request.type = args.type

        if args.access_key is not None:
            request.access_key = args.access_key

        if args.bucket is not None:
            request.bucket = args.bucket

        if args.secret_key is not None:
            request.secret_key = args.secret_key

        if args.endpoint_url is not None:
            request.endpoint_url = args.endpoint_url

        if args.insecure_https is not None:
            request.insecure_https = args.insecure_https

        if args.project is not None:
            request.project = args.project

        headers = {"Content-Type": "application/json"}
        assert found.id is not None
        api_instance.registries_id_put(found.id, request, _headers=headers)


@authentication.required
def delete_registry(args: Namespace) -> None:
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)
        found = lookup_registry(args.name, api_instance)
        assert found.id is not None
        api_instance.registries_id_delete(found.id)


def wrapped(description: str) -> str:
    """Wrap the description at nn characters."""
    try:
        width = int(os.getenv("AIOLI_MODEL_DESCRIPTION_WIDTH", "120"))
    except ValueError:
        raise cli.errors.CliError("AIOLI_MODEL_DESCRIPTION_WIDTH must be an integer")
    return "\n".join(textwrap.wrap(description, width=width))


def format_model(r: aiolirest.TrainedModelRegistry, m: aiolirest.ModelResponse) -> List[Any]:
    description = ""
    if m.description is not None:
        description = wrapped(m.description)
    if r.type == "openllm":
        # Strategy to reduce the output line width...
        # display_name is not much different to the uri we calculate and contains
        # a date/time stamp, so don't show that.
        # The description field isn't populated with anything very useful, but I
        # suppose that may change in time.
        # latest_version_id_str is in the calculated uri, so don't show that.
        # format shows a range of values, but for our users all are 'openllm'.
        return [m.url, description]
    if r.type == "huggingface":
        downloads = m.metadata.get("downloads") if m.metadata else None
        return [m.latest_version_id_str, m.url, downloads, m.format]
    # This leaves type == NGC
    return [
        m.display_name,
        m.image,
        bytes_to_gib(m.latest_version_size_in_bytes),
        description,
    ]


# Convert bytes to GiB for a more human-readable output.
def bytes_to_gib(size: Optional[StrictInt]) -> str:
    if size is None:
        return ""
    size2 = size / 1024 / 1024 / 1024
    return f"{size2:.1f}"


# Here is a list of known model formats, taken from the REST API documentation.
# As described there, in order to generate smaller query result sets we will query
# for models of each type in turn.
knownOpenllmModelFormats = [
    "baichuan",
    "chatglm",
    "dolly_v2",
    "falcon",
    "flan_t5",
    "gemma",
    "gpt_neox",
    "llama",
    "mistral",
    "mixtral",
    "mpt",
    "opt",
    "phi",
    "qwen",
    "stablelm",
    "starcoder",
    "yi",
]


@authentication.required
def list_models(args: Namespace) -> None:
    """Implements 'aioli registry models <registry-name>'

    which lists the available models in a registry.
    """
    with cli.setup_session(args) as session:
        api_instance = aiolirest.RegistriesApi(session)
        registry = lookup_registry(args.name, api_instance)

    models: List[aiolirest.ModelResponse] = []

    # The columns displayed depend on the registry type, so adjust the headers accordingly.
    headers = ["Name", "Image", "Size\nGiB", "Description"]
    assert registry.id is not None
    if registry.type == "openllm":
        formats = knownOpenllmModelFormats
        if args.format:
            formats = [args.format]
        headers = ["URL", "Description"]
        for model_format in formats:
            response = api_instance.registries_id_models_get(registry.id, model_format)
            for m in response:
                models.append(m)
    elif registry.type == "huggingface":
        headers = ["Name", "URL", "Downloads", "Model Type"]
        models = api_instance.registries_id_models_get(registry.id, args.search)
    else:
        models = api_instance.registries_id_models_get(registry.id, args.format)

    if args.json:
        render.print_json([m.to_dict() for m in models])
    elif args.yaml:
        print(render.format_object_as_yaml([m.to_dict() for m in models]))
    else:
        values = [format_model(registry, m) for m in models]
        render.tabulate_or_csv(headers, values, args.csv)


def upload_nim(args: Namespace) -> None:
    """Implements 'aioli upload-nim <nim-name> <s3-url>'"""

    name = args.dir
    s3_url = args.URL
    cache = os.path.expanduser(name)

    if not os.path.exists(cache):
        raise cli.errors.CliError(
            f"Cache directory {cache} does not exist. " "Please download the model profiles first."
        )
    if not s3_url.startswith("s3://"):
        raise cli.errors.CliError(f"S3 URL {s3_url} is not valid. It should start with 's3://'.")

    # Get the base file name from the path provided as name
    # Verify that the prefix is of the form models--org--team--modelname
    import re

    base = os.path.basename(name)
    pattern = r"^models--[a-zA-Z0-9]+--[a-zA-Z0-9]+--[a-zA-Z0-9\.\-_]+$"
    if not re.match(pattern, base):
        raise cli.errors.CliError(
            f"Invalid model name format: {base}. Expected format: models--org--team--modelname"
        )
    base = base[len("models--") :]
    model_name = base.replace("--", "/")

    print(f"Model name {model_name}")

    # Remove 's3://' prefix and split bucket/key
    s3_url_no_prefix = s3_url[5:]
    bucket = s3_url_no_prefix
    key_prefix = ""
    if "/" in s3_url_no_prefix:
        bucket, key_prefix = s3_url_no_prefix.split("/", 1)

    # For each file in the cache directory, upload it to the S3 bucket.
    for root, _, files in os.walk(cache):
        if os.path.basename(root) == "blobs":
            continue
        if os.path.basename(root) == "refs":
            continue
        print(f"Root {root}")
        for filename in files:
            dirName = os.path.basename(root)
            print(f"Processing {dirName} {filename}")

            local_path = os.path.join(root, filename)

            path = key_prefix + "/" or ""
            key = model_name
            key += ":" + dirName + "?file=" + filename

            # Use url encoding on the key to ensure it is valid for S3
            key = urllib.parse.quote_plus(key)
            key = path + key

            print(f"Uploading s3://{bucket}/{key}")
            # Perform the upload using boto3 (which supports .aws/config credentials)
            s3_client = boto3.client("s3")
            try:
                s3_client.upload_file(local_path, bucket, key)
            except boto3.exceptions.S3UploadFailedError as e:
                # Try to extract the error message if possible
                msg = getattr(e, "response", {}).get("Error", {}).get("Message", str(e))
                raise cli.errors.CliError(msg)
            except botocore.exceptions.BotoCoreError as e:
                # Try to extract the error message if possible
                msg = getattr(e, "response", {}).get("Error", {}).get("Message", str(e))
                raise cli.errors.CliError(
                    f"Failed to upload {local_path} to s3://{bucket}/{key}: {msg}"
                )
            except Exception as e:
                # Catch S3UploadFailedError and any other exception
                raise cli.errors.CliError(
                    f"Failed to upload {local_path} to s3://{bucket}/{key}: {str(e)}"
                )
            print(f"Uploaded {local_path} to s3://{bucket}/{key} successfully.")


main_cmd = Cmd(
    "registries r|egistry",
    None,
    "manage packaged model registries",
    [
        # Inspection commands.
        Cmd(
            "list ls",
            list_registries,
            "list registries",
            [
                Group(
                    Arg("--csv", action="store_true", help="print as CSV"),
                    Arg("--json", action="store_true", help="print as JSON"),
                    Arg("--yaml", action="store_true", help="print as YAML"),
                ),
            ],
            is_default=True,
        ),
        # Create command.
        Cmd(
            "create",
            create,
            "create a registry",
            [
                Arg(
                    "name",
                    help="The name of the model registry. Must begin with a letter, but may "
                    "contain letters, numbers, and hyphen",
                ),
                Arg("--type", help="The type of this model registry", required="true"),
                Arg("--bucket", help="S3 Bucket name"),
                Arg("--access-key", help="S3 access key/username"),
                Arg("--secret-key", help="secret key/password", required="true"),
                Arg("--endpoint-url", help="S3 endpoint URL"),
                Arg(
                    "--insecure-https",
                    help="Allow insecure HTTPS connections to S3",
                    action="store_true",  # prefer argparse.BooleanOptionalAction
                ),
                Arg("--project", help="The project this registry belongs to"),
            ],
        ),
        # Show command.
        Cmd(
            "show",
            show_registry,
            "show a registry",
            [
                Arg(
                    "name",
                    help="The name of the registry.",
                ),
                Group(
                    Arg("--yaml", action="store_true", help="print as YAML", default=True),
                    Arg("--json", action="store_true", help="print as JSON"),
                ),
            ],
        ),
        # Update command.
        Cmd(
            "update",
            update,
            "modify a registry",
            [
                Arg("registryname", help="The name of the model registry"),
                Arg(
                    "--name",
                    help="The new name of the model registry. Must begin with a letter, but may "
                    "contain letters, numbers, and hyphen",
                ),
                Arg("--type", help="The type of this model registry"),
                Arg("--bucket", help="S3 Bucket name"),
                Arg("--access-key", help="S3 access key/username"),
                Arg("--secret-key", help="S3 secret key/password"),
                Arg("--endpoint-url", help="S3 endpoint URL"),
                Arg(
                    "--insecure-https",
                    help="Allow insecure HTTPS connections to S3",
                    action="store_true",  # prefer argparse.BooleanOptionalAction
                ),
                Arg("--project", help="The project this registry belongs to"),
            ],
        ),
        Cmd(
            "delete",
            delete_registry,
            "delete a registry",
            [
                Arg("name", help="The name of the model registry"),
            ],
        ),
        Cmd(
            "model|s",
            list_models,
            "lists the available models in a registry (for certain registry types)",
            [
                Arg("name", help="The name of the model registry"),
                Arg(
                    "--search",
                    help="The optional string value that will be contained in the returned "
                    + "model names (huggingface only)",
                ),
                Arg(
                    "--format",
                    "--modelformat",
                    help="Model format to list from the registry (oppenllm or s3)",
                ),
                Group(
                    Arg("--csv", action="store_true", help="print as CSV"),
                    Arg("--json", action="store_true", help="print as JSON"),
                    Arg("--yaml", action="store_true", help="print as YAML"),
                ),
            ],
        ),
        Cmd(
            "upload-nim",
            upload_nim,
            argparse.SUPPRESS,
            # "Uploads the profiles associated with a NIM model "
            # + "from a local directory to an S3 bucket.",
            [
                Arg("dir", help="The root directory of the nim model in the local cache."),
                Arg(
                    "URL",
                    help="The S3 URL to upload the model -- "
                    + "aws auth config must already be setup.",
                ),
            ],
        ),
    ],
)

args_description = [main_cmd]  # type: List[Any]
