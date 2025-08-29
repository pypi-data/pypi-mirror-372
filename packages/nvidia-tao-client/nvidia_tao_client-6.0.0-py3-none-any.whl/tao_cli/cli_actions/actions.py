# Copyright (c) 2024, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""TAO-Client base actions module"""

import json
import requests
import os
import time

from configparser import ConfigParser

timeout = 3600 * 24


class Actions:
    """Base class which defines API functions for general actions"""

    def __init__(self):
        """Initialize the actions base class"""
        config = ConfigParser()
        config_file_path = os.path.join(os.path.expanduser("~"), ".tao", "config")
        config.read(config_file_path)
        default_org = os.getenv("ORG", "noorg")
        default_token = os.getenv("TOKEN", "invalid")
        default_base_url = os.getenv(
            "BASE_URL", "https://api.tao.ngc.nvidia.com/api/v1"
        )
        self.org_name = config.get("main", "ORG", fallback=default_org)
        self.token = config.get("main", "TOKEN", fallback=default_token)
        self.base_url = (
            config.get("main", "BASE_URL", fallback=default_base_url)
            + f"/orgs/{self.org_name}"
        )
        self.headers = {"Authorization": f"Bearer {self.token}"}

    # Workspace specific actions
    def workspace_create(self, name, cloud_type, cloud_details):
        """Create a dataset and return the id"""
        request_dict = {"name": name, "cloud_type": cloud_type}
        if cloud_details:
            request_dict["cloud_specific_details"] = json.loads(cloud_details)
        data = json.dumps(request_dict)
        endpoint = self.base_url + "/workspaces"
        response = requests.post(
            endpoint, data=data, headers=self.headers, timeout=timeout
        )
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        if "id" not in response.json().keys():
            print(f"ID not present in json response {response.json()}")
        assert "id" in response.json().keys()
        id = response.json()["id"]
        return id


    # Backup a workspace
    def workspace_backup(self, backup_file_name, workspace):
        """Backup a workspace"""
        endpoint = f"{self.base_url}/workspaces/{workspace}/backup"
        data = json.dumps({"backup_file_name": backup_file_name})
        response = requests.post(endpoint, data=data, headers=self.headers, timeout=timeout)
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        return response.json()


    # Restore a workspace
    def workspace_restore(self, backup_file_name, workspace):
        """Restore a workspace"""
        endpoint = f"{self.base_url}/workspaces/{workspace}/restore"
        data = json.dumps({"backup_file_name": backup_file_name})
        response = requests.post(endpoint, data=data, headers=self.headers, timeout=timeout)
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        return response.json()


    # Dataset specific actions
    def dataset_create(
        self, dataset_type, dataset_format, workspace, cloud_file_path, url, use_for
    ):
        """Create a dataset and return the id"""
        request_dict = {"type": dataset_type, "format": dataset_format}
        if workspace:
            request_dict["workspace"] = workspace
        if cloud_file_path:
            request_dict["cloud_file_path"] = cloud_file_path
        if url:
            request_dict["url"] = url
        if use_for:
            request_dict["use_for"] = json.loads(use_for)
        data = json.dumps(request_dict)
        endpoint = self.base_url + "/datasets"
        response = requests.post(
            endpoint, data=data, headers=self.headers, timeout=timeout
        )
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        if "id" not in response.json().keys():
            print(f"ID not present in json response {response.json()}")
        assert "id" in response.json().keys()
        id = response.json()["id"]
        return id

    # Experiment specific actions
    def experiment_create(self, network_arch, encryption_key, workspace):
        """Create an experiment and return the id"""
        request_dict = {
            "network_arch": network_arch,
            "encryption_key": encryption_key,
            "workspace": workspace,
        }
        data = json.dumps(request_dict)
        endpoint = self.base_url + "/experiments"
        response = requests.post(
            endpoint, data=data, headers=self.headers, timeout=timeout
        )
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        if "id" not in response.json().keys():
            print(f"ID not present in json response {response.json()}")
        assert "id" in response.json().keys()
        id = response.json()["id"]
        return id

    def list_base_experiments(self, params=""):
        """List the available datasets/experiments"""
        endpoint = self.base_url + "/experiments:base"
        if params:
            params = json.loads(params)
        response = requests.get(
            endpoint, params=params, headers=self.headers, timeout=timeout
        )
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        return response.json()["experiments"]

    # Common actions
    def list_artifacts(self, artifact_type, params=""):
        """List the available datasets/experiments"""
        endpoint = self.base_url + f"/{artifact_type}s"
        if params:
            params = json.loads(params)
        response = requests.get(
            endpoint, params=params, headers=self.headers, timeout=timeout
        )
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        return response.json()[f"{artifact_type}s"]

    def artifact_delete(self, artifact_type, artifact_id):
        """Delete a dataset/experiment"""
        endpoint = f"{self.base_url}/{artifact_type}s/{artifact_id}"
        response = requests.delete(endpoint, headers=self.headers, timeout=timeout)
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)

    def get_artifact_metadata(self, id, artifact_type):
        """Get metadata of experiment/dataset"""
        endpoint = f"{self.base_url}/{artifact_type}s/{id}"
        response = requests.get(endpoint, headers=self.headers, timeout=timeout)
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        return response.json()

    def patch_artifact_metadata(self, id, artifact_type, update_info):
        """Update metadata of a experiment/dataset"""
        endpoint = f"{self.base_url}/{artifact_type}s/{id}"
        update_info = json.loads(update_info)
        if (
            "automl_settings" in update_info
            and "automl_hyperparameters" in update_info["automl_settings"]
        ):
            update_info["automl_settings"]["automl_hyperparameters"] = str(
                update_info["automl_settings"]["automl_hyperparameters"]
            )
        response = requests.patch(
            endpoint, json=update_info, headers=self.headers, timeout=timeout
        )
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        return response.json()

    def get_action_spec(self, id, action, artifact_type):
        """Return spec dictionary for the action passed"""
        endpoint = self.base_url + f"/{artifact_type}s/{id}/specs/{action}/schema"
        while True:
            response = requests.get(endpoint, headers=self.headers, timeout=timeout)
            if response.status_code == 404:
                if "Base spec file download state is " in response.json()["error_desc"]:
                    print("Base experiment spec file is being downloaded")
                    time.sleep(2)
                    continue
                break
            break
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        data = response.json()["default"]
        return data

    def get_automl_defaults(self, id, action):
        """Return automl parameters enabled for a network"""
        endpoint = self.base_url + f"/experiments/{id}/specs/{action}/schema"
        response = requests.get(endpoint, headers=self.headers, timeout=timeout)
        data = response.json()["automl_default_parameters"]
        return data

    def run_action(self, id, parent_job, action, artifact_type, specs, platform_id):
        """Submit post request for an action"""
        request_dict = {
            "parent_job_id": parent_job,
            "action": action,
            "specs": json.loads(specs),
        }
        if platform_id:
            request_dict["platform_id"] = platform_id
        data = json.dumps(request_dict)
        endpoint = self.base_url + f"/{artifact_type}s/{id}/jobs"
        response = requests.post(
            endpoint, data=data, headers=self.headers, timeout=timeout
        )
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        job_id = response.json()
        return job_id

    def get_action_status(self, id, job, artifact_type):
        """Get status for an action"""
        endpoint = self.base_url + f"/{artifact_type}s/{id}/jobs/{job}"
        response = requests.get(endpoint, headers=self.headers, timeout=timeout)
        return response.json()

    def publish_model(
        self, id, job, artifact_type, display_name, description, team_name
    ):
        """Publish model to ngc registry"""
        endpoint = self.base_url + f"/{artifact_type}s/{id}/jobs/{job}:publish_model"
        request_dict = {
            "display_name": display_name,
            "description": description,
            "team_name": team_name,
        }
        data = json.dumps(request_dict)
        response = requests.post(
            endpoint, data=data, headers=self.headers, timeout=timeout
        )
        return response.json()

    def remove_published_model(self, id, job, artifact_type, team_name):
        """Remove published model from ngc registry"""
        endpoint = (
            self.base_url + f"/{artifact_type}s/{id}/jobs/{job}:remove_published_model"
        )
        params = {"team_name": team_name}
        response = requests.delete(
            endpoint, params=params, headers=self.headers, timeout=timeout
        )
        return response.json()

    def job_cancel(self, id, job, artifact_type):
        """Cancel a running job"""
        endpoint = self.base_url + f"/{artifact_type}s/{id}/jobs/{job}:cancel"
        response = requests.post(endpoint, headers=self.headers, timeout=timeout)
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)

    def job_pause(self, id, job, artifact_type):
        """Pause a running job"""
        endpoint = self.base_url + f"/{artifact_type}s/{id}/jobs/{job}:pause"
        response = requests.post(endpoint, headers=self.headers, timeout=timeout)
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)

    def job_resume(self, id, job_id, parent_job, specs):
        """Resume a paused job"""
        request_dict = {"parent_job_id": parent_job, "specs": json.loads(specs)}
        data = json.dumps(request_dict)
        endpoint = self.base_url + f"/experiments/{id}/jobs/{job_id}:resume"
        response = requests.post(
            endpoint, data=data, headers=self.headers, timeout=timeout
        )
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)

    def list_files_of_job(self, id, job, job_type, retrieve_logs, retrieve_specs):
        endpoint = f"{self.base_url}/{job_type}s/{id}/jobs/{job}:list_files"
        params = {"retrieve_logs": retrieve_logs, "retrieve_specs": retrieve_specs}
        response = requests.get(
            endpoint, headers=self.headers, params=params, timeout=timeout
        )
        if response.status_code not in (200, 201):
            print(
                f"Request failed with error code {response.status_code} and message: {response.text}"
            )
        assert response.status_code in (200, 201)
        return response.json()

    def job_download_selective_files(
        self,
        id,
        job,
        job_type,
        workdir,
        file_lists=[],
        best_model=False,
        latest_model=False,
        tar_files=True,
    ):
        """Download a job with the files passed"""
        endpoint = (
            f"{self.base_url}/{job_type}s/{id}/jobs/{job}:download_selective_files"
        )
        params = {
            "file_lists": file_lists,
            "best_model": best_model,
            "latest_model": latest_model,
            "tar_files": tar_files,
        }

        # Save
        temptar = f"{workdir}/{job}.tar.gz"
        if not tar_files and len(file_lists) == 1:
            temptar = os.path.join(workdir, job, file_lists[0])
        os.makedirs(os.path.dirname(temptar), exist_ok=True)
        with requests.get(
            endpoint, headers=self.headers, params=params, stream=True, timeout=timeout
        ) as r:
            r.raise_for_status()
            with open(temptar, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return temptar

    def entire_job_download(self, id, job, job_type, workdir):
        """Download a job"""
        endpoint = f"{self.base_url}/{job_type}s/{id}/jobs/{job}:download"

        # Save
        temptar = f"{workdir}/{job}.tar.gz"
        os.makedirs(os.path.dirname(temptar), exist_ok=True)
        with requests.get(endpoint, headers=self.headers, stream=True) as r:
            r.raise_for_status()
            with open(temptar, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return temptar

    def get_job_logs(self, id, job, job_type):
        """Return logs of a running job"""
        endpoint = f"{self.base_url}/{job_type}s/{id}/jobs/{job}/logs"
        response = requests.get(endpoint, headers=self.headers, timeout=timeout)
        if "Logs for the job are not available yet" in response.text:
            print("Logs for the job are not available yet")
            return
        if response.status_code not in (200, 201):
            print(f"Request failed with error code {response.status_code} and message: {response.text}")
        assert response.status_code in (200, 201), f"Request failed with error code {response.status_code} and message: {response.text}"
        for chunk in response.iter_content(chunk_size=8192, decode_unicode=True):
            print(chunk, end='')
