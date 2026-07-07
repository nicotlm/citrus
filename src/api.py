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

    def get_annonce_json(self, annonce_id):
        return json.loads(self.get_annonce(annonce_id).content).get("results")[0]


def _clean_json(json_dict):
    json_dict["listeprecedentproprietaire"] = json.loads(json_dict["listeprecedentproprietaire"])
    json_dict["listepersonnes"] = json.loads(json_dict["listepersonnes"])
    json_dict["listeetablissements"] = json.loads(json_dict["listeetablissements"])

    return json_dict


def parse_vente(json_dict):
    json_dict = _clean_json(json_dict)
    sireneCedant = "Erreur"
    raisonSocialeCedant = "Erreur"
    sirenBeneficiaire = "Erreur"
    raisonSocialeBeneficiaire = "Erreur"
    try:
        sireneCedant = json_dict["listeprecedentproprietaire"]["personne"]["numeroImmatriculation"]["numeroIdentification"].replace(" ", "")
    except Exception as e: 
        print(f"An error occurred: {e}")

    try:
        raisonSocialeCedant = json_dict["listeprecedentproprietaire"]["personne"]["denomination"]
    except Exception as e: 
        print(f"An error occurred: {e}")

    try:
        sirenBeneficiaire = json_dict["listepersonnes"]["personne"]["numeroImmatriculation"]["numeroIdentification"].replace(" ", "")
    except Exception as e: 
        print(f"An error occurred: {e}")

    try:
        raisonSocialeBeneficiaire = json_dict["listepersonnes"]["personne"]["denomination"]
    except Exception as e: 
        print(f"An error occurred: {e}")

    return {
        "sirenCedant": sireneCedant,
        "raisonSocialeCedant": raisonSocialeCedant,
        "sirenBeneficiaire": sirenBeneficiaire,
        "raisonSocialeBeneficiaire": raisonSocialeBeneficiaire,
        "source": json_dict["url_complete"]
    }

# 'montantNet' : en ke, à extraire depuis json.loads(json_dict['listeetablissements'])["etablissement"]["origineFonds"] ('siège et établissement principal acquis par achat au prix stipulé de 155000.00 euros')
# 'dateEffetComptable' : extraire depuis date de commencement ou commentaires ? défaut dateparution ?
# 'dateRealisationJuridique' : extraire depuis date de commencement ou commentaires ?
