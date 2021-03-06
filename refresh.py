from flask import Flask, request
from intuitlib.client import AuthClient
from google.cloud import bigquery
from quickbooks import QuickBooks
from quickbooks.objects import Customer
import json
import os

app = Flask( __name__ )

@app.route( '/' )
def refresh_tokens() :

    company_id = '9130352109852406'

    bq_client = bigquery.Client()

    query_job = bq_client.query(
        f"""
        SELECT *
        FROM `yetibooks-reporting.Utility.QBO_Secret_Store`
        WHERE company_id = '{ company_id }'
        """
    )

    results = query_job.result()

    for row in results :

        client_id = row.client_id
        client_secret = row.client_secret
        access_token = row.access_token
        environment = row.environment
        redirect_uri = row.redirect_url
        refresh_token = row.refresh_token

    # Instantiate auth client
    auth_client = AuthClient(
        client_id = client_id,
        client_secret = client_secret,
        access_token = access_token,
        environment = environment,
        redirect_uri = redirect_uri,
    )

    # Refresh tokens
    auth_client.refresh( refresh_token=refresh_token )

    access_token = auth_client.access_token
    refresh_token = auth_client.refresh_token

    update_job = bq_client.query(
        f"""
        UPDATE `yetibooks-reporting.Utility.QBO_Secret_Store`
            SET access_token = '{ access_token }'
               ,refresh_token = '{ refresh_token }'
        WHERE company_id = '{ company_id }'
        """
    )

    result = update_job.result()

    return 'ok', 200

if __name__ == "__main__" :
    app.run( host='0.0.0.0', port=int( os.getenv( 'PORT', 8080 )))

