from src.llm.client import ask_json
from src import logger


def _build_prompt_llm(text_a_extraire, instructions) -> list[dict]:

    system = (
        "Tu es un assistant pour extraire des informations d'un journal d'annonces légales. "
        "Tu reponds UNIQUEMENT avec un objet JSON valide, sans aucun texte ni "
        "balise Markdown autour. Par exemple si je te demande une balise 'montantNet': "
        '{{"montantNet": 330000}}"'
    )

    user = f"""A partir du contenu donné ci-après, renvoie un objet JSON avec exactement cette clé :

{instructions}


**Texte dont il faut extraire l'information**
{text_a_extraire}"""

    llm_prompt = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    logger.debug(f"LLM prompt is {llm_prompt}")
    return llm_prompt


def _build_prompt_llm_amount(text_a_extraire, instructions_exemple) -> list[dict]:

    instr = (
        '- "montantNet" : extrait le montant en euros uniquement à partir du texte' +
        ' ci dessous. Ne met pas de centimes ou de virgules, juste le montant en euros. ' +
        'Par exemple, pour le texte ' + "'" + str(instructions_exemple) + "'" +
        ' tu dois retourner {"montantNet": 330000}.'
    )

    return _build_prompt_llm(text_a_extraire=text_a_extraire, instructions=instr)


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
