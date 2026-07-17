"""
Ask the LLM to classify the type of restructuration of a BODACC annonce.

Usage:
    python classify_type.py                 # runs on a sample annonce id
    python classify_type.py A202601261236   # runs on a given annonce id
"""

import os
import sys

if os.getcwd() != "/home/onyxia/work/citrus" and os.path.isdir("citrus"):
    os.chdir("citrus")

from src.bodacc.api import bodacc_api
from src.operation.triage import (
    classify_type_operation,
    gather_operation_text,
    TYPE_OPERATION_LABELS,
)

# Default sample id (same one used in test.py).
annonce_id = sys.argv[1] if len(sys.argv) > 1 else "A202601261236"  # "A202500631070"

api = bodacc_api()
bodacc_annonce = api.get_annonce_json(annonce_id)

# What the classifier actually reads (useful to eyeball / debug the prompt).
print("----- Texte envoye au LLM -----")
print(gather_operation_text(bodacc_annonce))

# The classification itself.
type_operation = classify_type_operation(bodacc_annonce)
print("----- Resultat -----")
print(f"{annonce_id} -> {type_operation} ({TYPE_OPERATION_LABELS[type_operation]})")