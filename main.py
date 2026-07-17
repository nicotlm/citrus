from src.modele.metrics import filter_metrics_bad
from src.modele.evaluate import evaluate_vente

###########################
# Parsing operation Vente
###########################
source = "s3://projet-citrus/data/202607_citrus_bodacc_300ventes.csv"
# source = "s3://projet-citrus/data/202607_citrus_bodacc_1800op.csv"
from_bodacc_df, res, citrus_apibodacc_df = evaluate_vente(source)

different_rows = filter_metrics_bad(citrus_apibodacc_df, res, "raisonSocialeCedant")
print(different_rows)

different_rows = filter_metrics_bad(citrus_apibodacc_df, res, "dateEffetComptable")
print(different_rows)