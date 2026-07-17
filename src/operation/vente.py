from src.llm.prompt import _build_prompt_llm_amount
from src.llm.client import ask_json
from src import logger


def _build_prompt_llm_vente_amount(text_a_extraire) -> list[dict]:
    exemple_vente_amount = "Etablissement principal acquis par achat au prix stipulé de 330000 EUR"

    return _build_prompt_llm_amount(
        text_a_extraire=text_a_extraire,
        instructions_exemple=exemple_vente_amount
    )


def extract_amount_vente(json_dict):
    originefonds = json_dict.get("listeetablissements", {}).get("etablissement", {})
    if isinstance(originefonds, list):
        originefonds = originefonds[0].get("origineFonds", "")
    elif isinstance(originefonds, dict):
        originefonds = originefonds.get("origineFonds", "")
    else:
        originefonds = ""

    logger.info(f"Extracting amount from '{originefonds}'")
    return ask_json(
        _build_prompt_llm_vente_amount(originefonds)
    )
