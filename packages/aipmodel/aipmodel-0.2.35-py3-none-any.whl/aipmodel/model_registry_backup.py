import base64

import requests


class ModelRegistry:
    def __init__(self, endpint_url: str, access_key: str, secret_key: str, user_name: str):
        self.endpint_url = endpint_url
        encoded_cred = base64.b64encode(f"{access_key}:{secret_key}".encode())
        headers = {"Authorization": f"Basic {encoded_cred.decode()}"}
        res = requests.post(url=self.endpint_url + "/auth.login", headers=headers)
        self.access_token = res.json()["data"]["token"]
        self.user_name = user_name
        self.project_id = None

    def get_project(self):
        params = dict()
        params["name"] = f"model_registry_{self.user_name}"

        headers = {"Authorization": f"Bearer {self.access_token}"}
        res = requests.post(url=self.endpint_url + "/projects.get_all", headers=headers, params=params)
        res = res.json()["data"]["projects"]
        if len(res) > 0:
            self.project_id = res[0]["id"]
            return self.project_id
        return None

    def create_project(self):
        if self.get_project() is None:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            res = requests.post(
                url=self.endpint_url + "/projects.create",
                headers=headers,
                params={
                    "name": f"model_registry_{self.user_name}",
                    "description": f"Model Registery for {self.user_name}",
                },
            )
            print(res.json())
            self.project_id = res.json()["data"]["id"]
            return self.project_id
        return self.get_project()

    def delete_project(self):
        _id = self.get_project()
        if _id is not None:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            res = requests.post(
                url=self.endpint_url + "/projects.delete",
                headers=headers,
                params={
                    "project": _id,
                    "delete_contents": True,
                },
            )
        return _id

    def add_model(self, name: str, uri: str):
        _id = self.get_project()
        params = dict()
        params["name"] = name
        params["uri"] = uri
        params["project"] = _id

        headers = {"Authorization": f"Bearer {self.access_token}"}
        res = requests.post(url=self.endpint_url + "/models.create", headers=headers, params=params)
        return res.json()["data"]["id"]

    def delete_models(self, name: str):
        _id = self.get_project()
        models = self.get_models(name)
        deleted_models = []
        for model_info in models:
            params = dict()
            params["model"] = model_info["id"]
            headers = {"Authorization": f"Bearer {self.access_token}"}
            res = requests.post(url=self.endpint_url + "/models.delete", headers=headers, params=params)
            if "deleted" in res.json()["data"] and res.json()["data"]["deleted"]:
                deleted_models.append(params["model"])
        return deleted_models

    def get_models(self, name=None):
        _id = self.get_project()
        params = dict()
        if name is not None:
            params["name"] = name
        params["project"] = _id

        headers = {"Authorization": f"Bearer {self.access_token}"}
        res = requests.post(url=self.endpint_url + "/models.get_all", headers=headers, params=params)
        return res.json()["data"]["models"]


if __name__ == "__main__":
    model_registry = ModelRegistry(
        endpint_url="http://213.233.184.112:30008",
        access_key="0PSU1VV5RDQO70WNL03X068K6GW6L9",
        secret_key="OKMqh-GOVsfAUJXv5uiWiQi5vy7xPtuUgXqly6CNd2A_KdSDPiTAqqkPTMbXGgqE5Gc",
        user_name="armin",
    )
    # print("Access token:", model_registry.access_token)
    # print("All Projects:", model_registry.get_all_projects())
    print("Create Projects:", model_registry.create_project())
    print("Get Models:", model_registry.get_models())
    print(
        "Create Model:",
        model_registry.add_model(name="whisper", uri="s3://almmlops/models/whisper/whisper-large-v2-fa"),
    )
    # print("Get Models:", model_registry.get_models(name='whisper'))
    # print("Delete Model:", model_registry.delete_models(name='whisper'))
    # print("Current Projects:", model_registry.get_project())
    # print("Delete Projects:", model_registry.delete_project())
    # print("Current Projects:", model_registry.get_project())
