"""
Classify the type of restructuration described by a BODACC annonce.

This runs *before* we know which operation we are dealing with, so it cannot
rely on the vente-shaped cleaning done in ``src.bodacc.api._clean_json`` (that
one assumes ``listeprecedentproprietaire`` is present). Instead we gather the
free-text description wherever it lives in the payload and let the LLM pick a
category, following the same convention as ``src.operation.vente``.

Four categories, returned as short codes (``typeOperation``):
    - "TUP" : transmission universelle de patrimoine
    - "LG"  : location-gérance
    - "FU"  : fusion (AVIS DE PROJET DE FUSION, société absorbée / absorbante)
    - "VE"  : vente / cession (the default, "acquis par", "achat", ...)
"""

import json

from unidecode import unidecode

from src.llm.prompt import _build_prompt_llm_type_operation
from src.llm.client import ask_json
from src import logger


# Human-readable labels, handy for logs and downstream reporting.
TYPE_OPERATION_LABELS = {
    "VE": "Vente / cession",
    "FU": "Fusion",
    "TUP": "Transmission universelle de patrimoine",
    "LG": "Location-gérance",
}

# Subtrees of the annonce that may carry the free-text description, depending on
# the kind of operation. Some are stored as a JSON string in the API response.
_TEXT_SUBTREES = ("acte", "modificationsgenerales", "divers", "listeetablissements")

# Short top-level fields that give the classifier useful context.
_CONTEXT_KEYS = ("familleavis_lib", "typeavis_lib")

# Map the LLM answer (code *or* French label, accents/space insensitive) to a code.
_ALIASES = {
    "VE": "VE",
    "FU": "FU",
    "TUP": "TUP",
    "LG": "LG",
}


def _maybe_load(value):
    """Parse a value that may be a JSON string into a Python object, else return as-is."""
    if isinstance(value, str):
        stripped = value.strip()
        if stripped.startswith(("{", "[")):
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return value
    return value


def _collect_strings(node) -> list[str]:
    """Recursively collect every non-empty string leaf of a nested structure."""
    found = []
    node = _maybe_load(node)
    if isinstance(node, dict):
        for value in node.values():
            found.extend(_collect_strings(value))
    elif isinstance(node, list):
        for item in node:
            found.extend(_collect_strings(item))
    elif isinstance(node, str):
        text = node.strip()
        if text:
            found.append(text)
    return found


def gather_operation_text(json_dict: dict) -> str:
    """
    Concatenate the free-text description of a BODACC annonce, wherever it lives.

    A vente exposes its text under ``acte`` / ``listeetablissements.origineFonds``,
    while a fusion or a transmission universelle de patrimoine is usually described
    under ``modificationsgenerales`` or ``divers``. We therefore gather text from
    every plausible subtree and de-duplicate.
    """
    chunks = []

    for key in _CONTEXT_KEYS:
        value = json_dict.get(key)
        if isinstance(value, str) and value.strip():
            chunks.append(value.strip())

    for key in _TEXT_SUBTREES:
        if key in json_dict:
            chunks.extend(_collect_strings(json_dict[key]))

    # De-duplicate while preserving order.
    seen = set()
    unique_chunks = []
    for chunk in chunks:
        if chunk not in seen:
            seen.add(chunk)
            unique_chunks.append(chunk)

    return "\n".join(unique_chunks)


def _normalize_type(raw) -> str | None:
    """Turn an LLM answer into one of the canonical codes, or None if unrecognised."""
    if raw is None:
        return None
    key = unidecode(str(raw)).upper()
    key = "".join(ch for ch in key if ch.isalnum() or ch == "-")
    return _ALIASES.get(key)


def classify_type_operation(json_dict: dict, default: str = "VE") -> str:
    """
    Ask the LLM to classify the type of restructuration of a BODACC annonce.

    Args:
        json_dict: the raw annonce, as returned by ``bodacc_api.get_annonce_json``.
        default: code returned when no text is found or the answer is unusable.

    Returns:
        one of the codes in ``TYPE_OPERATION_LABELS`` ("VE", "FU", "TUP", "LG").
    """
    text = gather_operation_text(json_dict)
    if not text:
        logger.warning(f"No text found to classify operation type - defaulting to {default}")
        return default

    logger.info("Classifying operation type from gathered text")
    logger.debug(f"Text sent for classification: {text}")

    answer = ask_json(_build_prompt_llm_type_operation(text))
    type_operation = _normalize_type(answer.get("typeOperation"))

    if type_operation is None:
        logger.warning(
            f"Unexpected typeOperation answer {answer!r} - defaulting to {default}"
        )
        return default

    logger.info(
        f"Operation classified as {type_operation} ({TYPE_OPERATION_LABELS[type_operation]})"
    )
    return type_operation