
import os

if os.getcwd() != '/home/onyxia/work/citrus':
    os.chdir("citrus")

from src.api import bodacc_api, parse_vente
from src.llm_extract import extract_amount 
from src.metrics import calculate_metrics
import polars as pl

api = bodacc_api()

###########################
# Parsing operation Vente
###########################
source = "s3://projet-citrus/data/citrus_bodacc.csv"

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

l=[]
for row in df.iter_rows(named=True):
    bodac_annonce = api.get_annonce_json(row["num_bodacc"])
    regex_dict = parse_vente(bodac_annonce)
    llm_dict = extract_amount(bodac_annonce)
    full_dict = {"num_bodacc": row["num_bodacc"]} | regex_dict | llm_dict
    l.append(full_dict)

from_bodacc_df = pl.DataFrame(l)

from_bodacc_df = from_bodacc_df.with_columns((pl.col("montantNet")/1000).round()).cast({"montantNet": pl.Int64})

citrus_apibodacc_df = df.join(from_bodacc_df, on="num_bodacc", suffix="_apibodacc") 

calculate_metrics(citrus_apibodacc_df).mean()
print(citrus_apibodacc_df)
