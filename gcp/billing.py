import base64
from google.cloud import bigquery
from datetime import datetime, timedelta
from collections import namedtuple

Costs = namedtuple("Charges", ["date","cost", "credit", "charge"])

def report_gcp_daily_cost(PROJECT_ID, DATASET, TABLE,date=None):
    client = bigquery.Client(project=PROJECT_ID)

    # Calculate yesterday's date (UTC)
    if date is None:
        yesterday = datetime.utcnow().date() - timedelta(days=1)
    else:
        yesterday = date


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
        total_cost = next(iter(result)).total_cost or 0.0

        query_credit_job = client.query(credit_query)
        result = query_credit_job.result()
        total_credits = next(iter(result)).total_cost or 0.0

        
        return Costs(
            date=yesterday,
            cost=total_cost,
            credit=total_credits*-1,
            charge=total_cost + total_credits
        )

    except Exception as e:
        print(f"Error retrieving billing data: {str(e)}")
        raise