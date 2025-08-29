#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

from os import environ, getenv
from os import listdir as scan_dir
from os.path import isdir as is_folder
from shutil import rmtree as remove_dir
from typing import Dict, Optional, Union
from urllib.parse import parse_qs, urlparse

from datasets import Dataset, DatasetDict
from datasets import load_dataset as hf_load_dataset
from huggingface_hub import HfApi, get_token
from requests.adapters import HTTPAdapter


# Exception class to be raised when environment variable is not set
class EnvironmentVariableNotSetError(Exception):
    """Exception raised when environment variable is not set"""

    pass


global MLX_DATA_MANAGER_ENDPOINT_URL
global MLX_DATA_MANAGER_HOST

# Initialize global variables - will be set by login() or from environment variables
MLX_DATA_MANAGER_ENDPOINT_URL = None
MLX_DATA_MANAGER_HOST = None


def override_constants():
    global MLX_DATA_MANAGER_ENDPOINT_URL
    global MLX_DATA_MANAGER_HOST

    # If global variables haven't been set by login(), check environment variables
    if MLX_DATA_MANAGER_ENDPOINT_URL is None:
        # MLX_DATA_MANAGER_ENDPOINT_URL을 우선적으로 사용하고, 없으면 MLX_ENDPOINT_URL을 사용
        if "MLX_DATA_MANAGER_ENDPOINT_URL" in environ:
            MLX_DATA_MANAGER_ENDPOINT_URL = getenv("MLX_DATA_MANAGER_ENDPOINT_URL")
        elif "MLX_ENDPOINT_URL" in environ:
            MLX_ENDPOINT_URL = getenv("MLX_ENDPOINT_URL")
            MLX_DATA_MANAGER_ENDPOINT_URL = (
                f"{MLX_ENDPOINT_URL.rstrip('/')}/data-manager"
            )
        else:
            raise EnvironmentVariableNotSetError(
                "MLX_DATA_MANAGER_ENDPOINT_URL or MLX_ENDPOINT_URL environment variable is not set. "
                "Please set one of the environment variables or provide mdm_endpoint_url parameter to login(). "
            )

    # Set host if not already set
    if MLX_DATA_MANAGER_HOST is None:
        MLX_DATA_MANAGER_HOST = urlparse(MLX_DATA_MANAGER_ENDPOINT_URL).hostname

    # hub_env
    import huggingface_hub.constants as hc

    URL_SUFFIX = "/{repo_id}/resolve/{revision}/{filename}"

    from huggingface_hub.hf_api import api

    api.endpoint = f"{MLX_DATA_MANAGER_ENDPOINT_URL}"
    hc.ENDPOINT = f"{MLX_DATA_MANAGER_ENDPOINT_URL}"

    hc.HUGGINGFACE_CO_URL_HOME = hc.ENDPOINT
    hc.HUGGINGFACE_CO_URL_TEMPLATE = hc.ENDPOINT + URL_SUFFIX

    from huggingface_hub import file_download

    file_download.HUGGINGFACE_CO_URL_TEMPLATE = hc.ENDPOINT + URL_SUFFIX

    from datasets import config

    config.HF_ENDPOINT = hc.ENDPOINT


def clear_cache(path="."):
    for i in scan_dir(path):
        if is_folder(path + i):
            if i == "__pycache__":
                remove_dir(path + i)
            else:
                clear_cache(path + i)


def login(token, mdm_endpoint_url=None, *args, **kwargs):
    if mdm_endpoint_url:
        global MLX_DATA_MANAGER_HOST
        global MLX_DATA_MANAGER_ENDPOINT_URL

        MLX_DATA_MANAGER_HOST = urlparse(mdm_endpoint_url).hostname

        if "data-manager" in mdm_endpoint_url:
            MLX_DATA_MANAGER_ENDPOINT_URL = mdm_endpoint_url
        else:
            MLX_DATA_MANAGER_ENDPOINT_URL = (
                f"{mdm_endpoint_url.rstrip('/')}/data-manager"
            )

    from huggingface_hub import login as hf_login

    apply_env()

    return hf_login(token=token, *args, **kwargs)


def apply_env():
    override_constants()
    clear_cache(".")


def load_dataset(path, *args, **kwargs):
    apply_env()
    return hf_load_dataset(path, *args, **kwargs)


def get_api_object():
    apply_env()
    return HfApi()


def push_to_hub(
    self,
    repo_id: str,
    config_name: str = "default",
    set_default: Optional[bool] = None,
    data_dir: Optional[str] = None,
    commit_message: Optional[str] = None,
    commit_description: Optional[str] = None,
    private: Optional[bool] = False,
    token: Optional[str] = None,
    revision: Optional[str] = None,
    create_pr: Optional[bool] = False,
    max_shard_size: Optional[Union[int, str]] = None,
    num_shards: Optional[Dict[str, int]] = None,
    embed_external_files: bool = True,
):
    apply_env()
    DatasetDict.push_to_hub = huggingface_dataset_dict_push_to_hub
    Dataset.push_to_hub = huggingface_dataset_push_to_hub

    ret = self.push_to_hub(
        repo_id=repo_id,
        config_name=config_name,
        set_default=set_default,
        data_dir=data_dir,
        commit_message=commit_message,
        commit_description=commit_description,
        private=private,
        token=token,
        revision=revision,
        create_pr=create_pr,
        max_shard_size=max_shard_size,
        num_shards=num_shards,
        embed_external_files=embed_external_files,
    )
    DatasetDict.push_to_hub = push_to_hub
    Dataset.push_to_hub = push_to_hub

    return ret


huggingface_dataset_dict_push_to_hub = DatasetDict.push_to_hub
huggingface_dataset_push_to_hub = Dataset.push_to_hub
DatasetDict.push_to_hub = push_to_hub
Dataset.push_to_hub = push_to_hub

_original_send = HTTPAdapter.send


def custom_send(self, request, *args, **kwargs):
    if (
        "authorization" not in request.headers.keys()
        and MLX_DATA_MANAGER_HOST in request.url
    ):
        parsed_url = urlparse(request.url)
        query_params = parse_qs(parsed_url.query)
        if "X-Amz-Algorithm" not in query_params:
            request.headers["authorization"] = f"Bearer {get_token()}"
    return _original_send(self, request, *args, **kwargs)


# Monkey patch
HTTPAdapter.send = custom_send  # type: ignore
