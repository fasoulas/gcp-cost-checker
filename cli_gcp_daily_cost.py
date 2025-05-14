import base64
from google.cloud import bigquery
from datetime import datetime, timedelta
import os
import sys

DATASET = os.environ.get("BILLING_DATASET")
TABLE = os.environ.get("BILLING_TABLE")
PROJECT_ID = os.environ.get("GCP_BILLING_PROJECT_ID")

def slack_gcp_daily_cost(event, context):
    return report_gcp_daily_cost


def validate_inputs():
    DATASET = os.environ.get("BILLING_DATASET")
    TABLE = os.environ.get("BILLING_TABLE")
    PROJECT_ID = os.environ.get("GCP_BILLING_PROJECT_ID")

    if DATASET is None:
        print(f'BILLING_DATASET env variable is missing')
        sys.exit(1)
    if TABLE is None:
        print(f'BILLING_TABLE env variable is missing')
        sys.exit(1)
    if PROJECT_ID is None:
        print(f'CP_BILLING_PROJECT_ID env variable is missing')
        sys.exit(1)

    print('All environment variables are set correctly.')

def report_gcp_daily_cost():
    client = bigquery.Client(project=PROJECT_ID)

    # Calculate yesterday's date (UTC)
    yesterday = datetime.utcnow().date() - timedelta(days=1)

    cost_query = f"""
        SELECT
            SUM(cost) as total_cost
        FROM `{DATASET}.{TABLE}`
        WHERE
            usage_start_time >= TIMESTAMP('{yesterday} 00:00:00')
            AND usage_start_time < TIMESTAMP('{yesterday + timedelta(days=1)} 00:00:00')
    """

    credit_query = f"""
       SELECT
            SUM(IFNULL((SELECT SUM(credit.amount) FROM UNNEST(credits) AS credit), 0)) AS total_cost,
        FROM `{DATASET}.{TABLE}`
        WHERE
           usage_start_time >= TIMESTAMP('{yesterday} 00:00:00')
            AND usage_start_time < TIMESTAMP('{yesterday + timedelta(days=1)} 00:00:00')
    """

    try:
        query_cost_job = client.query(cost_query)
        result = query_cost_job.result()
        total_cost = next(result).total_cost or 0.0

        query_credit_job = client.query(credit_query)
        result = query_credit_job.result()
        total_credits = next(result).total_cost or 0.0

        print(f"Total GCP cost for [{yesterday}]: £{total_cost:.2f}")
        print(f"Total GCP credits for [{yesterday}]: £{total_credits*-1:.2f}")
        print(f"Total GCP payable charges for [{yesterday}]: £{total_cost+total_credits:.2f}")


    except Exception as e:
        print(f"Error retrieving billing data: {str(e)}")
        raise

if __name__ == "__main__":
  validate_inputs()
  report_gcp_daily_cost()