from src.llm_client import ask_json
from src import logger


def _build_prompt_llm(text_a_extraire) -> list[dict]:

    system = (
        "Tu es un assistant pour extraire des informations d'un journal d'annonces légales. "
        "Tu reponds UNIQUEMENT avec un objet JSON valide, sans aucun texte ni "
        "balise Markdown autour."
    )

    intro = "A partir du contenu donné ci-après, renvoie un objet JSON avec exactement cette clé :"
    amount_instr = (
        '- "montantNet" : extrait le montant en euros uniquement à partir du texte',
        'ci dessous. Ne met pas de centimes ou de virugles, juste le montant en euros',
        'Par exemple, pour le texte "Etablissement principal acquis par achat au ',
        'prix stipulé de 330000 EUR" tu dois retourner {"montantNet": 330000}'
    )

    user = f"""{intro}

{amount_instr}

\"\"\"
{text_a_extraire}
\"\"\"

Reponds uniquement avec le JSON, par exemple :
{{"montantNet": 330000}}"""

    llm_prompt = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    logger.debug(f"LLM prompt is {llm_prompt}")
    return llm_prompt


def extract_amount(json_dict):
    originefonds = json_dict.get("listeetablissements", {}).get("etablissement", {})
    if isinstance(originefonds, list):
        originefonds = originefonds[0].get("origineFonds", "")
    elif isinstance(originefonds, dict):
        originefonds = originefonds.get("origineFonds", "")
    else:
        originefonds = ""

    logger.info(f"Extracting amount from '{originefonds}'")
    return ask_json(
        _build_prompt_llm(originefonds)
    )
