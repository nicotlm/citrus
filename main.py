
from src.api import bodacc_api, parse_vente
# import src.llm_client as llm_client

import polars as pl
import os

if os.getcwd() != '/home/onyxia/work/citrus':
    os.chdir("citrus")

api = bodacc_api()


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

print(parse_vente(api.get_annonce_json(df[0, "num_bodacc"])))

