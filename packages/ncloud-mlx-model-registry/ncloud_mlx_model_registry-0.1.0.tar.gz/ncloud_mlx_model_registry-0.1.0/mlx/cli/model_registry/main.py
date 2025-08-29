#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import datetime
import logging
import logging.config
import os
import time
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import timeago
import typer
from dateutil.parser import parse
from rich import print as rich_print
from rich.console import Console
from rich.filesize import decimal
from rich.text import Text
from rich.tree import Tree
from typing_extensions import Annotated

from mlx.api import model_registry
from mlx.sdk.model_registry.api import HealthApi, ModelRegistryAPI
from mlx.sdk.model_registry.version import version

from .context import Context
from .errors import EmptyCurrentProjectError
from .printer import created_message, deleted_message, pretty_table, pretty_yaml

LOGGER_NAME = "mlx.cli.model_registry"
logger = logging.getLogger(LOGGER_NAME)

err_console = Console(stderr=True)

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])
app = typer.Typer(
    name="model-registry",
    short_help="Model registry command line interface",
    no_args_is_help=True,
    context_settings=CONTEXT_SETTINGS,
)


class ModelRegistryGlobalContext:
    debug: bool
    parent_obj: Any


@app.callback()
def _main(
    ctx: typer.Context,
    debug: bool = typer.Option(
        False, "--debug", "-d", help="If set print debug messages"
    ),
):
    own_ctx_obj = ModelRegistryGlobalContext()
    if ctx.obj:
        own_ctx_obj.parent_obj = ctx.obj

    own_ctx_obj.debug = debug
    if hasattr(ctx.obj, "debug") and ctx.obj.debug:
        own_ctx_obj.debug |= ctx.obj.debug

    ctx.obj = own_ctx_obj

    if ctx.obj.debug:
        LOGGING_CONFIG = {
            "version": 1,
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "http",
                    "stream": "ext://sys.stderr",
                }
            },
            "formatters": {
                "http": {
                    "format": "%(levelname)s [%(asctime)s] %(name)s - %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "loggers": {
                "root": {
                    "handlers": ["default"],
                    "level": "DEBUG",
                },
                "httpx": {
                    "level": "DEBUG",
                },
                "httpcore": {
                    "level": "DEBUG",
                },
                "urllib3": {
                    "level": "DEBUG",
                },
                "http.client": {
                    "level": "DEBUG",
                },
                "mlx.api.model_registry": {
                    "level": "DEBUG",
                },
                "mlx.cli.model_registry": {
                    "level": "DEBUG",
                },
                "mlx.sdk.model_registry": {
                    "level": "DEBUG",
                },
            },
        }
        logging.config.dictConfig(LOGGING_CONFIG)

        logger.debug(f"VERSION : {version}")


mlx_app = app

if __name__ == "__main__":
    app()


def convert_labels_to_dict(labels: List[str]) -> Dict:
    ret = {}
    for label in labels:
        key, value = label.split("=")
        ret[key] = value
    return ret


ARG_MODEL_NAME = Annotated[str, typer.Argument(help="Model name string")]
ARG_VERSION_NAME = Annotated[str, typer.Argument(help="Version name string")]

ARG_DESCRIPTION = Annotated[
    Optional[str],
    typer.Option(
        "--description",
        "-d",
        help="Description string",
    ),
]

ARG_SUMMARY = Annotated[
    Optional[str],
    typer.Option(
        "--summary",
        "-s",
        help="Summary string",
    ),
]
ARG_TAGS = Annotated[List[str], typer.Option("--tag", "-t", help="Tag string")]
ARG_LABELS = Annotated[
    List[str],
    typer.Option("--label", "-l", help="Label string (key=value format)"),
]
ARG_UNTAGS = Annotated[List[str], typer.Option("--untag", help="Remove the tag")]
ARG_UNLABELS = Annotated[
    List[str],
    typer.Option("--unlabel", help="Remove the label(key)"),
]  # TODO: add normalize callback
ARG_STORAGE_CLASS = Annotated[
    Optional[str],
    typer.Option(
        "--storage-class",
        help="Storage type to use - supported: [warm, cold]",
    ),
]


create_command = typer.Typer(
    name="create",
    short_help="Model or version create",
    no_args_is_help=True,
)

app.add_typer(create_command, no_args_is_help=True)


@create_command.command(name="model", no_args_is_help=True)
def create_model(
    ctx: typer.Context,
    modelname: ARG_MODEL_NAME,
    description: ARG_DESCRIPTION = None,
    summary: ARG_SUMMARY = None,
    tags: ARG_TAGS = [],
    labels: ARG_LABELS = [],
    storage_class: ARG_STORAGE_CLASS = None,
):
    """
    Create model on model registry service
    """
    context = Context()

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    projectname = context.current_project
    if not projectname:
        raise EmptyCurrentProjectError

    model_request = model_registry.ModelRequest(
        name=modelname,
        description=description,
        summary=summary,
        labels=convert_labels_to_dict(labels),
        tags=tags,
        storage=storage_class,
    )

    model_response = mr_api.model_api.create(projectname, model_request)
    typer.echo(created_message(model_response, "model", modelname))


class Stage(str, Enum):
    dev = "DEV"
    stage = "STAGE"
    produection = "PRODUCTION"


ARG_AUTHOR = Annotated[
    Optional[str], typer.Option("--author", "-a", help="Author name")
]
ARG_STAGE = Annotated[Stage, typer.Option("--stage", help="Stage string")]

ARG_TRAINING_ENVIRONMENT_DOCKERIMAGE = Annotated[
    str, typer.Option(help="Training environment docker image")
]
ARG_TRAINING_ENVIRONMENT_HOSTOS = Annotated[
    str, typer.Option(help="Training environment host os")
]
ARG_TRAINING_ENVIRONMENT_PACKAGES = Annotated[
    List[str],
    typer.Option(help="Training environment package"),
]
ARG_TRAINING_REFERENCE = Annotated[
    str,
    typer.Option(
        help="Training reference",
    ),
]
ARG_TRAINING_SOURCE_COMMITID = Annotated[
    str,
    typer.Option(
        help="Training source commit id",
    ),
]
ARG_TRAINING_SOURCE_REPO = Annotated[
    str,
    typer.Option(
        help="Training source repo",
    ),
]


@create_command.command(name="version")
def create_version(
    ctx: typer.Context,
    modelname: ARG_MODEL_NAME,
    version: ARG_MODEL_NAME,
    author: ARG_AUTHOR = None,
    stage: Optional[ARG_STAGE] = None,
    summary: ARG_SUMMARY = None,
    tags: ARG_TAGS = [],
    training_environment_dockerimage: ARG_TRAINING_ENVIRONMENT_DOCKERIMAGE = "",
    training_environment_hostos: ARG_TRAINING_ENVIRONMENT_HOSTOS = "",
    training_environment_packages: ARG_TRAINING_ENVIRONMENT_PACKAGES = [],
    training_reference: ARG_TRAINING_REFERENCE = "",
    training_source_commitid: ARG_TRAINING_SOURCE_COMMITID = "",
    training_source_repo: ARG_TRAINING_SOURCE_REPO = "",
    labels: ARG_LABELS = [],
):
    """
    Create version of model on model registry service
    """

    # Check if stage option is used and show warning
    if stage is not None:
        typer.echo(
            "Warning: --stage option is not currently implemented on the server. "
            "This feature will be supported in the future. "
            "Other fields will be processed normally.",
            err=True
        )
        stage = ""

    context = Context()

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    projectname = context.current_project
    if not projectname:
        raise EmptyCurrentProjectError

    assert_exist_model(mr_api, projectname, modelname)

    training = model_registry.Training(
        environment=model_registry.Environment(
            dockerImage=training_environment_dockerimage,
            hostOS=training_environment_hostos,
            packages=training_environment_packages,
        ),
        reference=training_reference,
        source=model_registry.Source(
            commitId=training_source_commitid,
            repo=training_source_repo,
        ),
    )

    model_version_request = model_registry.VersionRequest(
        version=version,
        author=author,
        labels=convert_labels_to_dict(labels),
        stage=stage,
        summary=summary,
        tags=tags,
        training=training,
    )

    resp = mr_api.model_version_api.create(
        projectname,
        modelname,
        model_version_request,
    )

    typer.echo(created_message(resp, "version", version))


@app.command()
def get(
    ctx: typer.Context,
    modelname: ARG_MODEL_NAME = "",
    version: ARG_VERSION_NAME = "",
    files: Annotated[
        bool,
        typer.Option(
            "--files",
            "-f",
            help="Print file list of model version",
        ),
    ] = False,
    recursive: Annotated[
        bool,
        typer.Option(
            "--recursive",
            "-r",
            help="Print file list recursively",
        ),
    ] = False,
    information: Annotated[
        bool,
        typer.Option(
            "--information",
            "-i",
            help="Print file information",
        ),
    ] = False,
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-l",
            help="Item count limitation number to print (only model, version)",
        ),
    ] = 30,
    search: Annotated[
        str,
        typer.Option(
            "--search",
            "-s",
            help="string to search model or version name",
        ),
    ] = "",
    all: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="If set, print all model (ignore --limit option)",
        ),
    ] = False,
):
    """
    Print model or version's details
    """

    context = Context()

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    projectname = context.current_project
    if not projectname:
        raise EmptyCurrentProjectError

    if modelname == "":
        m = mr_api.model_api.list(projectname, page_size=limit, search=search)
        models = m.models

        if all and models and m.total_count and m.total_count > len(models):
            m = mr_api.model_api.list(
                projectname, page_size=m.total_count, search=search
            )
            models = m.models

        print_models(models)
        print_total_count_remain_warning(all, m.total_count, limit)

        return

    if version == "":
        assert_exist_model(mr_api, projectname, modelname)

        m = mr_api.model_api.get(projectname, modelname)
        print_model(m)

        vs = mr_api.model_version_api.list(
            projectname, modelname, page_size=limit, search=search
        )

        versions = vs.model_versions

        if all and versions and vs.total_count and vs.total_count > len(versions):
            vs = mr_api.model_version_api.list(
                projectname, modelname, page_size=vs.total_count, search=search
            )
            versions = vs.model_versions

        print_model_versions(versions)
        print_total_count_remain_warning(all, vs.total_count, limit)

        return

    if not files:
        assert_exist_version(mr_api, projectname, modelname, version)
        v = mr_api.model_version_api.get(projectname, modelname, version)
        print_model_version(v)

    else:
        print_file_tree(
            mr_api,
            projectname,
            modelname,
            version,
            recursive,
            information,
        )


@app.command(name="list")
def list_models(
    ctx: typer.Context,
    modelname: ARG_MODEL_NAME = "",
    limit: Annotated[
        int,
        typer.Option(
            "--limit",
            "-l",
            help="Item count limitation number to print (only model, version)",
        ),
    ] = 30,
    all: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="If set, print all model (ignore --limit option)",
        ),
    ] = False,
):
    """
    List all models on model registry service
    """

    return get(
        ctx=ctx,
        modelname=modelname,
        limit=limit,
        all=all,
    )


def print_file_tree(
    mr_api: ModelRegistryAPI,
    projectname: str,
    modelname: str,
    version: str,
    recursive: bool,
    information: bool,
):
    total_size = 0
    file_count = 0
    dir_count = 0
    t = Tree(f"[green]:file_cabinet: {projectname}/{modelname}/{version}")
    tree_dict = {}
    tree_dict["/"] = t
    for dir, file in mr_api.file_api._list_remote_items(
        projectname,
        modelname,
        version,
        "/",
        recursive=recursive,
        file_only=False,
    ):
        if file.is_dir:
            parent_node = os.path.dirname(dir)
            node = tree_dict[parent_node].add(f"[green]:file_folder: {file.name}")
            tree_dict[dir] = node
            dir_count += 1
        else:
            parent_node = os.path.dirname(dir)
            file_row = Text(f"📄 {file.name}")
            if information:
                last_updated = parse(file.last_updated)
                updated_ago = timeago.format(
                    last_updated, datetime.datetime.now(datetime.timezone.utc)
                )
                file_row.append(f" ({decimal(file.size)}, {updated_ago})", "#808080")

            tree_dict[parent_node].add(file_row)
            file_count += 1
            total_size += file.size

    rich_print(t)
    if recursive:
        rich_print(
            f"    Dir: {dir_count}  "
            f"File: {file_count}  "
            f"Size: {decimal(total_size)} ({total_size} bytes)"
        )


update_command = typer.Typer(
    name="update",
    short_help="Update model or version on model registry service",
    no_args_is_help=True,
)
app.add_typer(update_command, no_args_is_help=True)


@update_command.command(name="model", no_args_is_help=True)
def update_model(
    ctx: typer.Context,
    modelname: ARG_MODEL_NAME,
    description: ARG_DESCRIPTION = None,
    summary: ARG_SUMMARY = None,
    labels: ARG_LABELS = [],
    unlabels: ARG_UNLABELS = [],
    tags: ARG_TAGS = [],
    untags: ARG_UNTAGS = [],
):
    """
    Update model information
    """

    context = Context()

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    projectname = context.current_project
    if not projectname:
        raise EmptyCurrentProjectError

    resp = mr_api.model_api.get(projectname, modelname)

    model_request = model_registry.ModelUpdateRequest(
        description=(description != "") and description or resp.description,
        summary=(summary != "") and summary or resp.summary,
        labels=new_labels(resp.labels, convert_labels_to_dict(labels), unlabels),
        tags=new_tags(resp.tags, tags, untags),
    )

    updated_model = mr_api.model_api.update(
        projectname,
        modelname,
        model_request,
    )

    print_model(updated_model)


def new_labels(old_labels: Dict, add_labels: Dict, unlabels: List[str]) -> Dict:
    labels = {}
    if old_labels:
        labels.update(old_labels)

    if add_labels:
        labels.update(add_labels)

    for ut in unlabels:
        try:
            del labels[ut]
        except KeyError:
            # OK. label key does not exist
            pass

    if not labels:
        # empty labels has no effect to model registry server,
        # so if new labels is empty, add Empty key
        # for deleting exist keys on server's labels
        labels = {}

    return labels


def new_tags(old_tags: List[str], add_tags: List[str], untags: List[str]) -> List[str]:
    tags = list((set(old_tags or []) | set(add_tags or [])) - set(untags or []))

    if not tags:
        tags = []
    return tags


@update_command.command(name="version")
def update_version(
    ctx: typer.Context,
    modelname: ARG_MODEL_NAME,
    version: ARG_VERSION_NAME,
    author: ARG_AUTHOR = None,
    labels: ARG_LABELS = [],
    unlabels: ARG_UNLABELS = [],
    stage: Optional[ARG_STAGE] = None,
    summary: ARG_SUMMARY = None,
    tags: ARG_TAGS = [],
    untags: ARG_UNTAGS = [],
    training_environment_dockerimage: ARG_TRAINING_ENVIRONMENT_DOCKERIMAGE = "",
    training_environment_hostos: ARG_TRAINING_ENVIRONMENT_HOSTOS = "",
    training_environment_package: ARG_TRAINING_ENVIRONMENT_PACKAGES = [],
    training_reference: ARG_TRAINING_REFERENCE = "",
    training_source_commitid: ARG_TRAINING_SOURCE_COMMITID = "",
    training_source_repo: ARG_TRAINING_SOURCE_REPO = "",
):
    """
    Update version information
    """

    context = Context()

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    projectname = context.current_project
    if not projectname:
        raise EmptyCurrentProjectError

    resp = mr_api.model_version_api.get(
        projectname,
        modelname,
        version,
    )

    # Check if stage update is attempted and show warning
    if stage is not None:
        typer.echo(
            "Warning: --stage option is not currently implemented on the server. "
            "This feature will be supported in the future. "
            "Other fields will be updated normally.",
            err=True
        )

    # Check if summary update is attempted and show warning
    if summary is not None and summary != "":
        typer.echo(
            "Warning: Summary field update is currently not supported for "
            "version updates. This feature will be fixed in a future "
            "release. Other fields will be updated normally.",
            err=True
        )

    model_version_request = model_registry.VersionUpdateRequest(
        author=(author != "") and author or resp.author,
        labels=new_labels(resp.labels, convert_labels_to_dict(labels), unlabels),
        stage=(stage != "") and stage or resp.stage,
        summary=(summary != "") and summary or resp.summary,
        tags=new_tags(resp.tags, tags, untags),
    )

    updated_version = mr_api.model_version_api.update(
        projectname,
        modelname,
        version,
        model_version_request,
    )

    print_model_version(updated_version)


@app.command(no_args_is_help=True)
def delete(
    ctx: typer.Context,
    modelname: Annotated[str, typer.Argument(help="Model name to delete")],
    version: Annotated[str, typer.Argument(help="Version name to delete")] = "",
    remote_path: Annotated[str, typer.Argument(help="Remote path to delete")] = "",
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="If set, no confirm")
    ] = False,
):
    """
    Delete a model, version, file or directory on model service
    """

    context = Context()

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    projectname = context.current_project
    if not projectname:
        raise EmptyCurrentProjectError

    if version == "":
        if not yes:
            input_model_name = typer.prompt(
                f"Please enter the model name({modelname}) to delete again",
            )
            if input_model_name != modelname:
                raise typer.Exit(1)
        # delete model
        mr_api.model_api.delete(projectname, modelname)
        typer.echo(deleted_message("", "model", modelname))
        return

    if remote_path == "":
        if not yes:
            input_version_name = typer.prompt(
                f"Please enter the version({version}) to delete again",
            )
            if input_version_name != version:
                raise typer.Exit(1)
        # delete version
        mr_api.model_version_api.delete(  # noqa: E501
            projectname, modelname, version
        )
        typer.echo(deleted_message("", "version", version))
        return

    # delete file
    if not yes:
        typer.confirm(
            f"Are you sure to delete files({remote_path}) of {modelname}/{version}?",
            default=False,
            abort=True,
        )

    mr_api.file_api.delete(
        project_name=projectname,
        model_name=modelname,
        version_name=version,
        file_name=remote_path,
    )
    typer.echo(deleted_message(None, f"{modelname}/{version}", remote_path))


ARG_LOCAL_PATH = Annotated[
    Path,
    typer.Argument(
        exists=True,
        file_okay=True,
        dir_okay=True,
        writable=False,
        readable=True,
        resolve_path=False,
        allow_dash=False,
    ),
]

ARG_REMOTE_PATH = Annotated[
    str, typer.Option("--remote-path", help="Remote path to upload")
]

ARG_OVERWRITE = Annotated[
    bool, typer.Option("--overwrite", "-o", help="If set, overwrite exist file(s)")
]

ARG_PARALLEL = Annotated[
    int, typer.Option("--parallel", "-p", help="Parallel count number", min=1, max=512)
]

ARG_INCLUDES = Annotated[
    List[str],
    typer.Option(
        "--includes",
        "-i",
        help="Unix filename pattern or full Path string to include. "
        "See https://docs.python.org/3/library/fnmatch.html for Unix filename pattern",
    ),
]

ARG_EXCLUDES = Annotated[
    List[str],
    typer.Option(
        "--excludes",
        "-e",
        help="Unix filename pattern or full Path string to exclude",
    ),
]

ARG_DRY_RUN = Annotated[
    bool,
    typer.Option(
        "--dry-run",
        help="If set, run with no effect",
    ),
]

ARG_SKIP_UPLOAD_IF_EXIST = Annotated[
    bool,
    typer.Option(
        "--skip-if-exist",
        "-s",
        help="If set flag, skip uploading the file if it already exists",
    ),
]


@app.command()
def upload(
    ctx: typer.Context,
    modelname: ARG_MODEL_NAME,
    version: ARG_VERSION_NAME,
    local_path: ARG_LOCAL_PATH,
    remote_path: ARG_REMOTE_PATH = "/",
    overwrite: ARG_OVERWRITE = False,
    parallel: ARG_PARALLEL = 1,
    includes: ARG_INCLUDES = [],
    excludes: ARG_EXCLUDES = [],
    dry_run: ARG_DRY_RUN = False,
    skip_if_exist: ARG_SKIP_UPLOAD_IF_EXIST = False,
):
    """
    Upload file or directory to model registry service
    """

    context = Context()

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    projectname = context.current_project

    assert_exist_version(
        mr_api=mr_api, projectname=projectname, modelname=modelname, version=version
    )

    mr_api.file_api.upload_sync(
        projectname,
        modelname,
        version,
        local_path.as_posix(),
        remote_path,
        includes=includes,
        excludes=excludes,
        overwrite=overwrite,
        parallel=parallel,
        dry_run=dry_run,
        skip_if_exist=skip_if_exist,
    )

    if dry_run or includes or excludes:
        return

    retry = 3
    wait_seconds = 1
    file_comp_list = None
    verified = False
    while retry > 0:
        verified, file_comp_list = mr_api.file_api.verify_upload(
            projectname,
            modelname,
            version,
            local_path.as_posix(),
            remote_path,
            includes=includes,
            excludes=excludes,
            overwrite=overwrite,
        )
        retry -= 1
        if verified or retry == 0:
            break
        time.sleep(wait_seconds)
        wait_seconds = wait_seconds * 2

    if not verified:
        typer.echo("Upload succeeded but verification failed")
        typer.echo(pretty_table(format_file_comp_list(file_comp_list)))
        raise typer.Exit(1)


ARG_DOWNLOAD_REMOTE_PATH = Annotated[
    str,
    typer.Option(
        "--remote-path",
        help="Remote path to download (relative path from model's root)",
    ),
]

ARG_OUTPUT_PATH = Annotated[
    Path,
    typer.Argument(
        exists=False,
        file_okay=True,
        dir_okay=True,
        writable=True,
        readable=True,
        resolve_path=False,
        allow_dash=False,
    ),
]

ARG_USE_HTTP = Annotated[
    bool,
    typer.Option(
        "--use-http",
        help="If set flag, download model file contents via HTTP protocol(not HTTPS)",
    ),
]

ARG_SKIP_IF_EXIST = Annotated[
    bool,
    typer.Option(
        "--skip-if-exist",
        "-s",
        help="If set flag, skip downloading the file if it already exists",
    ),
]


@app.command()
def download(
    ctx: typer.Context,
    modelname: ARG_MODEL_NAME,
    version: ARG_VERSION_NAME,
    output_path: ARG_OUTPUT_PATH,
    remote_path: ARG_DOWNLOAD_REMOTE_PATH = ".",
    overwrite: ARG_OVERWRITE = False,
    parallel: ARG_PARALLEL = 1,
    includes: ARG_INCLUDES = [],
    excludes: ARG_EXCLUDES = [],
    dry_run: ARG_DRY_RUN = False,
    use_http: ARG_USE_HTTP = False,
    skip_if_exist: ARG_SKIP_IF_EXIST = False,
):
    """
    Download a file or directory from model registry service

    Examples:

    \b
        ❯ # Suppose to the model files hierarchy below
        ❯ mlx mo get test v2 -fr
        🗄 gildong-hong/test/v2
        ├── 📄 a.json
        ├── 📄 b.json
        ├── 📄 c.pb
        ├── 📄 d.pb
        └── 📁 folder_a
            ├── 📄 a.json
            ├── 📄 b.json
            ├── 📄 c.pb
            └── 📄 d.pb
    \b
        ❯ # Download all files
        ❯ mlx model-registry download test v2 ./temp
    \b
        ❯ # Download a.json in root folder only
        ❯ mlx model-registry download test v2 ./temp -i "a.json"
    \b
        ❯ # Download *.json files in root folder
        ❯ mlx model-registry download test v2 ./temp -i "*.json" -e "/*/*.json"
    \b
        ❯ # Download all *.json including children folders
        ❯ mlx model-registry download test v2 ./temp -i "*.json"
    \b
        ❯ # Download specific folder
        ❯ mlx model-registry download test v2 ./temp -i "/folder_a/*"
    """

    context = Context()

    projectname = context.current_project

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    assert_exist_version(
        mr_api=mr_api, projectname=projectname, modelname=modelname, version=version
    )

    mr_api.file_api.download_sync(
        projectname,
        modelname,
        version,
        remote_path,
        output_path.as_posix(),
        overwrite=overwrite,
        parallel=parallel,
        includes=includes,
        excludes=excludes,
        dry_run=dry_run,
        use_http=use_http,
        skip_if_exist=skip_if_exist,
    )

    if dry_run:
        return

    verified, file_comp_list = mr_api.file_api.verify_download(
        projectname,
        modelname,
        version,
        remote_path,
        output_path.as_posix(),
        includes=includes,
        excludes=excludes,
    )

    if not verified:
        typer.echo("Download succeeded but verification failed")
        typer.echo(pretty_table(format_file_comp_list(file_comp_list)))
        raise typer.Exit(1)


def format_file_comp_list(list, time_compare=False) -> List[Dict]:
    ret = []
    for lfile, lfile_info, rfile, rfile_info in list.each():
        ret.append(
            {
                "LOCAL (size)": format_file_info(lfile, lfile_info),
                "LOCAL Updated at": lfile_info.last_updated if lfile else "",
                "<>": format_compare(lfile_info, rfile_info, time_compare),
                "REMOTE (size)": format_file_info(rfile, rfile_info),
                "REMOTE Updated at": rfile_info.last_updated if rfile else "",
            }
        )
    return ret


def format_file_info(path, info) -> str:
    if not path:
        return "---"
    return f"{path} " + typer.style(f"({info.size})", fg="cyan")


def format_compare(info_a, info_b, time_compare) -> str:
    if not info_a:
        return typer.style(">>", fg="yellow")

    if not info_b:
        return typer.style("<<", fg="yellow")

    if info_a.size != info_b.size:
        return typer.style("!=", fg="red")

    if time_compare and info_a.last_updated < info_b.last_updated:
        return typer.style("!=", fg="red")

    return "=="


ARG_COMPARE_TIMESTAMP = Annotated[
    bool,
    typer.Option(
        "--compare-timestamp",
        "-t",
        help="fail if the remote timestamp is newer than local",
    ),
]


@app.command()
def verify(
    ctx: typer.Context,
    modelname: ARG_MODEL_NAME,
    version: ARG_VERSION_NAME,
    local_path: ARG_LOCAL_PATH,
    compare_timestamp: ARG_COMPARE_TIMESTAMP = True,
):
    """
    Verify the local path's model file set with the model registry's file set

    """
    context = Context()

    projectname = context.current_project

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    verified, file_comp_list = mr_api.file_api.verify_download(
        projectname,
        modelname,
        version,
        "",
        local_path.as_posix(),
    )

    if compare_timestamp:
        for _, lfile_info, _, rfile_info in file_comp_list.each(
            local_only=False,
            remote_only=False,
        ):
            if lfile_info.last_updated < rfile_info.last_updated:
                # If set compare_timestamp,
                # Verification failed when a local file is older than it's remote file.
                verified = False
                break

    typer.echo(
        f"Model File Set Same : {typer.style(verified, fg='green' if verified else 'red')}"  # noqa: E501
    )
    typer.echo(pretty_table(format_file_comp_list(file_comp_list, compare_timestamp)))

    if not verified:
        raise typer.Exit(1)


def print_total_count_remain_warning(all: bool, total_count: int, limit: int):
    if all:
        return

    if total_count > limit:
        rich_print(
            "[yellow]"
            f"There are {total_count} items in total. "
            f"{total_count - limit} of them were not printed. "
            f"Set the --all option to print all items."
            "[/]"
        )








ARG_PROJECT_NAME = Annotated[
    str,
    typer.Option(
        "--project-name",
        "-p",
        help="specify the project name if you want uri for another project (not current project)",  # noqa: E501
    ),
]


@app.command(name="uri")
def uri(
    ctx: typer.Context,
    model_name: ARG_MODEL_NAME,
    version: ARG_VERSION_NAME,
    project_name: ARG_PROJECT_NAME = "",
):
    """
    Print uri for MODEL_NAME and VERSION to access model registry
    """

    context = Context()

    mr_api = get_model_registry_api(context, debug=ctx.obj.debug)

    if not project_name:
        project_name = context.current_project

    typer.echo(mr_api.model_version_api.uri(project_name, model_name, version))


def print_models(models: List[Any]):
    typer.secho("Model List", bold=True)
    # Fix to flatten storage class
    # for m in models:
    #     if m.storage:
    #         m.storage = m.storage.var_class
    typer.echo(
        pretty_table(
            [r.to_dict() for r in models],
            omits=["id", "description"],
            high_prior=["project", "name"],
        )
    )


def print_model(model):
    typer.secho("Model Information", bold=True)
    typer.echo(
        pretty_yaml(
            model,
            initial_indent=4,
            omit=["id"],
            high_prior=["name", "project"],
            omit_empty=False,
        )
    )


def print_model_versions(versions: List[Any]):
    typer.secho("Version List", bold=True)
    typer.echo(
        pretty_table(
            [r.to_dict() for r in versions],
            omits=["id", "training"],
            high_prior=["project", "model", "versionName"],
        )
    )


def print_model_version(version):
    typer.secho("Version Information", bold=True)
    typer.echo(
        pretty_yaml(
            version,
            initial_indent=4,
            high_prior=["project", "model", "version_name", "stage", "upload_done"],
            omit=["id"],
        )
    )


def print_model_version_files(files):
    typer.secho("Files List", bold=True)
    typer.echo(
        pretty_table(
            [r.to_dict() for r in files],
            high_prior=["name", "is_dir"],
        )
    )


def get_model_registry_api(context: Context, token="", debug=False) -> ModelRegistryAPI:
    ret = ModelRegistryAPI(
        api_endpoint=context.api_endpoint,
        access_token=token if token else context.access_token,
        debug=False,  # SEE below
    )

    if debug:
        # In debugging mode, the log level for all submodules is forcibly
        # changed to debug within the module. Since we only want to
        # configure urllib3, we create an instance and
        # then separately configure urllib3.
        logging.getLogger("urllib3").setLevel(logging.DEBUG)

    return ret


def assert_exist_model(
    mr_api: ModelRegistryAPI,
    projectname: str,
    modelname: str,
):
    if not mr_api.model_api.exist(projectname, modelname):
        err_console.print(
            f"Not found model for [bold red]{modelname}[/] in {projectname}"
        )
        raise typer.Exit(1)


def assert_exist_version(
    mr_api: ModelRegistryAPI,
    projectname: str,
    modelname: str,
    version: str,
):
    assert_exist_model(mr_api, projectname, modelname)
    if not mr_api.model_version_api.exist(projectname, modelname, version):
        err_console.print(
            f"Not found version for [bold red]{modelname}/{version}[/] in {projectname}"
        )
        raise typer.Exit(1)


@app.command()
def status(
    ctx: typer.Context,
    redact: Annotated[
        bool,
        typer.Option(help="Don't show token value."),
    ] = True,
):
    """
    Print status of config and context for model registry
    """

    context = Context()

    health_api = get_model_registry_api(context, debug=ctx.obj.debug).health_check_api

    rich_print("Model Regsitry Client Status")
    rich_print("  Current Project : ", context.current_project)
    rich_print("  API Endpoint    : ", context.api_endpoint)
    rich_print("  Access Token    : ", redact_string(context.access_token, not redact))
    rich_print("  Access Check    : ", access_check(health_api))


def redact_string(s: Optional[str], no_redact: bool) -> Optional[str]:
    if no_redact or not s:
        return s
    return s[:10] + "*" * 32


def access_check(health_api: HealthApi) -> Optional[str]:
    try:
        health_api.check().to_str()
        return "🟢 OK"
    except Exception as e:
        return e
