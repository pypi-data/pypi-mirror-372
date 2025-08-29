#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging

import requests

from xenoslib.base import ArgMethodBase
from xenoslib.extend import RequestAdapter, YamlConfig


logger = logging.getLogger(__name__)


class OneDrive(RequestAdapter):
    """
    onedrive for business with certain accounts
    https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/?view=odsp-graph-online
    """

    base_url = "https://graph.microsoft.com/v1.0"
    auth_url_template = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token"

    # https://portal.azure.com/#blade/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
    tenant = "0dc0acdd-87c8-4aa5-b794-f7918e012b77"
    client_id = "5195c197-4ad7-47e1-abf6-1e86d53f9dec"
    client_secret = "b467Q~Zi1Svi0s2aksB2HHK-Uk~YAHjCTumXx"

    def __init__(self, username=None, password=None):
        self.session = requests.Session()
        if username and password:
            res_data = self.auth(username, password)
            self.load_auth(res_data)

    def auth(self, username, password):
        """https://docs.microsoft.com/zh-cn/azure/active-directory/develop/v2-oauth-ropc"""
        auth_url = self.auth_url_template.format(tenant=self.tenant)
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": username,
            "password": password,
            "scope": "user.read openid profile offline_access",
            "grant_type": "password",
        }
        response = self.session.post(auth_url, data=data)
        response.raise_for_status()
        return response.json()

    def load_auth(self, res_data):
        self.session.headers.update(
            {
                "Authorization": f'Bearer {res_data["access_token"]}',
                "Accept": "application/json",
            }
        )

    def drives(self):
        return self.get("/me/drives/")

    def list(self, path="/"):
        for item in self.get(f"/me/drive/root:/{path}:/children")["value"]:
            item_type = "<DIR>" if item.get("folder") else ""
            print(f"{item_type}\t{item['name']}")

    def get_path(self, item_path):
        return self.get(f"/me/drive/root:/{item_path}")

    def content(self, item_path):
        """https://learn.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_get_content?view=odsp-graph-online"""
        path = f"/me/drive/root:/{item_path}:/content"
        url = f"{self.base_url}/{path}"
        return self.session.request("get", url, stream=True)

    def download(self, item_path):
        path, filename = os.path.split(item_path)
        with open(filename, "wb") as w:
            response = self.content(item_path)
            size = int(response.headers["content-length"])
            print(f"Total size: {size}")
            chunk_size = 1024**2
            for n, chunk in enumerate(response.iter_content(chunk_size=chunk_size), start=1):
                if chunk:
                    w.write(chunk)
                percentage = min(n * chunk_size / size * 100, 100)
                print(f"download progress: {percentage:.2f}% {filename}", end="\r")
            print()

    def mkdir(self):
        data = {
            "name": "New Folder",
            "folder": {},
            "@microsoft.graph.conflictBehavior": "rename",
        }
        return self.post("/me/drive/root/children", json=data)

    def rename(self, from_path=None, to_name=None):
        data = {
            "name": to_name,
            "parentReference": {},
        }
        return self.patch(f"/me/drive/root:/{from_path}", json=data)

    def upload_file(self, filepath, folder="/"):
        """
        https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_put_content?view=odsp-graph-online
        upload file with size uplimit to 4M, to upload bigger file use upload_bigfile()
        """
        with open(filepath, "rb") as r:
            data = r.read()
            return self.put(f"/me/drive/root:/{folder}/{filepath}:/content", data=data)

    def create_upload_session(self, filepath, folder="/"):
        """
        https://docs.microsoft.com/zh-cn/onedrive/developer/rest-api/api/driveitem_createuploadsession?view=odsp-graph-online
        """
        data = {"item": {"@microsoft.graph.conflictBehavior": "rename"}}
        res = self.post(f"/me/drive/root:{folder}/{filepath}:/createUploadSession", json=data)
        return res.get("uploadUrl")

    def upload(self, filepath, folder="/"):
        total_chunk = os.path.getsize(filepath)
        if total_chunk < 4 * 1024 * 1024:
            return self.upload_file(filepath, folder)
        return self.upload_bigfile(filepath, total_chunk, folder)

    def upload_bigfile(self, filepath, total_chunk, folder="/", chunk_size=60 * 1024 * 1024):
        url = self.create_upload_session(filepath, folder)
        with open(filepath, "rb") as r:
            current_chunk = 0
            while current_chunk < total_chunk:
                data = r.read(chunk_size)
                chunk_end = min(current_chunk + chunk_size - 1, total_chunk - 1)
                headers = {
                    "Content-Range": f"bytes {current_chunk}-{chunk_end}/{total_chunk}"
                }  # 'Content-Range': 'bytes 0-25/128'
                logger.debug(f"Content-Range: {headers['Content-Range']}")
                res = self.session.put(url=url, headers=headers, data=data)
                current_chunk += chunk_size
            return res.json()


class OneCLI(OneDrive):
    def upload(self, filepath, folder="/"):
        print(f"Uploading {filepath}...")
        return super().upload(filepath, folder)

    def get_conf_file(self):
        if os.name == "nt":
            home = os.path.expandvars("$userprofile")
        else:
            home = os.path.expandvars("$HOME")
        self.conf_file = os.path.join(home, ".one.yml")
        return self.conf_file

    def __init__(self, username=None, password=None, *args, **kwargs):
        self.session = requests.Session()
        self.get_conf_file()
        conf = YamlConfig(self.conf_file)
        if username and password:
            res_data = self.auth(username, password)
            self.load_auth(res_data)
            conf.update(res_data)
            conf.save()
        elif conf:
            self.load_auth(conf)
        else:
            print("no login")
            exit(-1)

    def logout(self):
        os.remove(self.conf_file)


class ArgMethod(ArgMethodBase):
    """onedrive tenant util"""

    @staticmethod
    def login(username, password):
        OneCLI(username, password)

    @staticmethod
    def logout():
        OneCLI().logout()

    @staticmethod
    def upload(filepath, folder="/"):
        """upload files to onedrive, not support folder yet"""
        import glob

        one = OneCLI()
        if "*" in filepath:
            for filename in glob.glob(filepath):
                print(one.upload(filename, folder=folder))
        elif os.path.isdir(filepath):
            for filename in glob.glob(f"{filepath}/**", recursive=True):
                if os.path.isfile(filename):
                    print(one.upload(filename, folder=folder))
        else:
            print(one.upload(filepath, folder=folder))

    @staticmethod
    def download(remote_path):
        OneCLI().download(remote_path)

    @staticmethod
    def down(remote_path):
        OneCLI().download(remote_path)

    @staticmethod
    def list(path="/"):
        OneCLI().list(path)

    @staticmethod
    def get(path="/"):
        try:
            print(OneCLI().get_path(path))
        except Exception as exc:
            print(exc)
            return False
        return True


if __name__ == "__main__":
    ArgMethod()
