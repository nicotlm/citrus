from src.api import bodacc_api
import src.llm_client as llm_client

api = bodacc_api()

api.get_annonce_content("B202601261710")