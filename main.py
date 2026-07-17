
import os

if os.getcwd() != "/home/onyxia/work/citrus":
    os.chdir("citrus")

from src.bodacc.api import bodacc_api, parse_vente
from src.operation.vente import extract_amount_vente
from src.metrics import calculate_metrics, filter_metrics_bad, _clean_string
import polars as pl

api = bodacc_api()

###########################
# Parsing operation Vente
###########################
source = "s3://projet-citrus/data/202607_citrus_bodacc_300ventes.csv"
# source = "s3://projet-citrus/data/202607_citrus_bodacc_1800op.csv"

df = pl.scan_csv(
    source,
    storage_options={
        "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
        "aws_region": "us-east-1",
    },
    credential_provider=pl.CredentialProviderAWS(
        profile_name="service-account",
        region_name="us-east-1",
    ),
).collect()

df = df.with_columns(
    pl.col("lien_bodacc").str.replace("https://www.bodacc.fr/annonce/detail-annonce/", "").str.replace_all("/", "").alias("num_bodacc")
)

res_list = []
for row in df.iter_rows(named=True):
    bodac_annonce = api.get_annonce_json(row["num_bodacc"])
    regex_dict = parse_vente(bodac_annonce)
    llm_dict = extract_amount_vente(bodac_annonce)
    full_dict = {"num_bodacc": row["num_bodacc"]} | regex_dict | llm_dict
    res_list.append(full_dict)

from_bodacc_df = pl.DataFrame(res_list)

from_bodacc_df = from_bodacc_df.with_columns((pl.col("montantNet")/1000).round(mode="half_away_from_zero")).cast({"montantNet": pl.Int64})

from_bodacc_df = _clean_string(from_bodacc_df, cols=["raisonSocialeCedant", "raisonSocialeBeneficiaire"])
citrus_apibodacc_df = df.join(from_bodacc_df, on="num_bodacc", suffix="_apibodacc")
print(citrus_apibodacc_df)

res = calculate_metrics(citrus_apibodacc_df)
print(res.mean())

different_rows = filter_metrics_bad(citrus_apibodacc_df, res, "raisonSocialeCedant")
print(different_rows)

with open("data/res.txt", "w") as f:
    f.write(f"Métriques:\n\n{str(res.mean())}\n\nLignes différentes:\n\n{str(different_rows)}")


