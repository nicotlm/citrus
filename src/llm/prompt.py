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
        'Par exemple, ' + str(instructions_exemple)
    )

    return _build_prompt_llm(text_a_extraire=text_a_extraire, instructions=instr)


def _build_prompt_llm_type_operation(text_a_extraire) -> list[dict]:

    instr = (
        '- "typeOperation" : determine le type de restructuration decrit dans le '
        "texte ci-dessous. Reponds avec EXACTEMENT l'un de ces quatre codes :\n"
        '    * "TUP" : transmission universelle de patrimoine. A utiliser lorsque '
        'le texte mentionne une "transmission universelle de patrimoine" (ou une '
        'formulation tres proche, par ex. "transmission universelle de son '
        'patrimoine").\n'
        '    * "LG" : location-gerance. A utiliser lorsque le texte mentionne une '
        '"location-gerance" / "location gerance" (mise en location-gerance, fin de '
        "location-gerance, contrat de location-gerance, etc.).\n"
        '    * "FU" : fusion. A utiliser lorsque le texte mentionne un projet ou un '
        'avis de fusion, par ex. "AVIS DE PROJET DE FUSION", "projet commun de '
        'fusion", une "societe absorbee" et une "societe absorbante".\n'
        '    * "VE" : vente / cession. A utiliser pour TOUS les autres cas de '
        "restructuration, en particulier les ventes et cessions de fonds. Le texte "
        'contient souvent "acquis par", "achat au prix stipule", "achat", '
        '"cession" ou "vente".\n'
        'En cas de doute entre "VE" et une autre categorie, ne choisis une autre '
        "categorie que si son mot-cle caracteristique est reellement present dans le "
        'texte ; sinon reponds "VE". '
        'Par exemple, pour le texte "Etablissement principal acquis par achat au '
        "prix stipule de 330000 EUR\", tu dois retourner {'typeOperation': 'VE'}."
    )

    return _build_prompt_llm(text_a_extraire=text_a_extraire, instructions=instr)


def _build_prompt_llm_date_comptable(
    text_a_extraire,
    instructions_exemple,
    instructions_complementaires=""
) -> list[dict]:

    instr = (
        '- "dateEffetComptable" : extrait la date uniquement à partir du texte' +
        ' ci dessous. Renvoie la date dans le format JJ-MM-AAAA. ' + str(instructions_complementaires) +
        'Par exemple, ' + str(instructions_exemple)
    )

    return _build_prompt_llm(text_a_extraire=text_a_extraire, instructions=instr)
