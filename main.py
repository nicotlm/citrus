
import os

if os.getcwd() != "/home/onyxia/work/citrus":
    os.chdir("citrus")

from src.bodacc.api import bodacc_api
from src.operation.vente import parse_vente, extract_amount_vente
from src.metrics import calculate_metrics, filter_metrics_bad, _clean_string
from src.utils import parse_to_date_df

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

df = parse_to_date_df(df, "dateEffetComptable")

res_list = []
for row in df.iter_rows(named=True):
    bodac_annonce = api.get_annonce_json(row["num_bodacc"])
    regex_dict = parse_vente(bodac_annonce)
    llm_dict = extract_amount_vente(bodac_annonce)
    full_dict = {"num_bodacc": row["num_bodacc"]} | regex_dict | llm_dict
    res_list.append(full_dict)

from_bodacc_df = pl.DataFrame(res_list, schema={
    'num_bodacc': pl.Utf8, 
    'anneeCampagne': pl.Int64, 
    'sirenCedant': pl.Utf8, 
    'raisonSocialeCedant': pl.Utf8,
    'sirenBeneficiaire': pl.Utf8,
    'raisonSocialeBeneficiaire': pl.Utf8,
    'dateEffetComptable': pl.Utf8,
    'typeOperation': pl.Utf8,
    'source': pl.Utf8,
    'montantNet': pl.Int64})

from_bodacc_df = from_bodacc_df.with_columns((pl.col("montantNet")/1000).round(mode="half_away_from_zero")).cast({"montantNet": pl.Int64})

from_bodacc_df = _clean_string(from_bodacc_df, cols=["raisonSocialeCedant", "raisonSocialeBeneficiaire"])
from_bodacc_df = parse_to_date_df(from_bodacc_df, "dateEffetComptable", format="%Y-%m-%d")

citrus_apibodacc_df = df.join(from_bodacc_df, on="num_bodacc", suffix="_apibodacc")
print(citrus_apibodacc_df)

citrus_apibodacc_df.write_csv(
    "s3://projet-citrus/data/202607_citrus_bodacc_300ventes_extraction.csv",
    storage_options={
        "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
        "aws_region": "us-east-1",
    },
    credential_provider=pl.CredentialProviderAWS(
        profile_name="service-account",
        region_name="us-east-1",
    )
)

res = calculate_metrics(citrus_apibodacc_df)
print(res.mean())

res.mean().write_csv(
    "s3://projet-citrus/data/202607_citrus_bodacc_300ventes_metrics.csv",
    storage_options={
        "aws_endpoint_url": "https://minio.lab.sspcloud.fr",
        "aws_region": "us-east-1",
    },
    credential_provider=pl.CredentialProviderAWS(
        profile_name="service-account",
        region_name="us-east-1",
    )
)

different_rows = filter_metrics_bad(citrus_apibodacc_df, res, "raisonSocialeCedant")
print(different_rows)

different_rows = filter_metrics_bad(citrus_apibodacc_df, res, "dateEffetComptable")
print(different_rows)