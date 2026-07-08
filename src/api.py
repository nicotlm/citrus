import requests
import json
from src import logger


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
        logger.info(f"Fetching info from {request_url} for annonce {annonce_id}")
        try:
            response = requests.get(request_url)
        except requests.exceptions.RequestException as e:
            logger.warning(f'Request failed with error {e}')
            response = None

        return response

    def get_annonce_json(self, annonce_id):
        annonce_content = self.get_annonce(annonce_id).content
        logger.info("Extracting results from annonce content")
        return json.loads(annonce_content).get("results")[0]


def _keep_numero_immat(personnes) -> list: 
    personnes_with_immat = []
    if isinstance(personnes, list):
        logger.debug(f"Cleaning {personnes} as a list")
        for personne in personnes:
            if personne.get("numeroImmatriculation"):
                personnes_with_immat.append(personne)
    elif isinstance(personnes, dict):
        logger.debug(f"Cleaning {personnes} as a dict")
        if personnes.get("numeroImmatriculation"):
            personnes_with_immat.append(personnes) 

    return personnes_with_immat


def _clean_json(json_dict):
    """
    Clean the response from API : transforms dict as dict 
    """
    logger.info("Cleaning listeprecedentproprietaire")
    json_dict["listeprecedentproprietaire"] = json.loads(json_dict["listeprecedentproprietaire"])
    json_dict["listeprecedentproprietaire_filtered"] = _keep_numero_immat(json_dict["listeprecedentproprietaire"].get("personne", []))

    logger.info("Cleaning listepersonnes")
    json_dict["listepersonnes"] = json.loads(json_dict["listepersonnes"])
    json_dict["listepersonnes_filtered"] = _keep_numero_immat(json_dict["listepersonnes"].get("personne", []))

    logger.info("Cleaning listeetablissements")
    json_dict["listeetablissements"] = json.loads(json_dict["listeetablissements"])

    return json_dict


def _get_siren(json_dict, key="listeprecedentproprietaire_filtered"):
    """
    Extract from JSON dict the first Siren from defined key (either listeprecedentproprietaire or listepersonnes)
    """
    logger.debug(f"Extracting Sirene from {json_dict.get(key, {})}")
    sirene = (json_dict.get(key, {})[0]
        .get("numeroImmatriculation", {})
        .get("numeroIdentification", {})
        .replace(" ", "")
        )
    return sirene


def _get_rs(json_dict, key="listeprecedentproprietaire_filtered"):
    """
    Extract from JSON dict the first raison sociale from defined key (either listeprecedentproprietaire or listepersonnes)
    """
    logger.debug(f"Extracting raison sociale from {json_dict.get(key, {})}")
    return json_dict[key][0].get("denomination", "")


def parse_vente(json_dict):
    """
    Extract from JSON dict sireneCedant, raisonSocialeCedant, sirenBeneficiaire, raisonSocialeBeneficiaire
    """
    logger.info("Cleaning json_dict")
    logger.debug(f"json_dict is {json_dict}")
    json_dict = _clean_json(json_dict)
    sireneCedant = _get_siren(json_dict, key="listeprecedentproprietaire_filtered")
    raisonSocialeCedant = _get_rs(json_dict, key="listeprecedentproprietaire_filtered")
    sirenBeneficiaire = _get_siren(json_dict, key="listepersonnes_filtered")
    raisonSocialeBeneficiaire = _get_rs(json_dict, key="listepersonnes_filtered")

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
