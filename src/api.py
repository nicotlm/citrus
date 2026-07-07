import requests
import json


class bodacc_api:
    def __init__(self, dataset_id="annonces-commerciales", end_point="records"):
        hook = "https://bodacc-datadila.opendatasoft.com/api/explore/v2.1/catalog/datasets"
        
        if end_point:
            self.url = f"{hook}/{dataset_id}/{end_point}"
        else:
            self.url = f"{hook}/{dataset_id}"

    def requests_url(self, annonce_id):
        return f"{self.url}?where=id%3D%22{annonce_id}%22&limit=1&offset=0&timezone=UTC&include_links=false&include_app_metas=false"

    def get_annonce(self, annonce_id):
        request_url = self.requests_url(annonce_id)
        response = requests.get(request_url)
        return response

    def get_annonce_content(self, annonce_id):
        return json.loads(self.get_annonce(annonce_id).content).get("results")[0]

