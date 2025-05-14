import os
import sys
from  gcp import billing as gcp_billing


DATASET = os.environ.get("BILLING_DATASET")
TABLE = os.environ.get("BILLING_TABLE")
PROJECT_ID = os.environ.get("GCP_BILLING_PROJECT_ID")


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



if __name__ == "__main__":
  validate_inputs()
  cost = gcp_billing.report_gcp_daily_cost(PROJECT_ID, DATASET, TABLE)
  print(f'Cost for [{cost.date}] is: £{cost.cost:.2f}')
  print(f'Credit for [{cost.date}] is: £{cost.credit:.2f}')
  print(f'Final charge for [{cost.date}] is: £{cost.charge:.2f}')