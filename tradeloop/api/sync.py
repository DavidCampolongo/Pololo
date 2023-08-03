from http.server import BaseHTTPRequestHandler
import csv
import requests
import time
import hashlib
import hmac
import json
from supabase import create_client, Client

# Connect to Supabase (service role - warning)
url = "https://xnqhlyvwofkcgbylgrzj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhucWhseXZ3b2ZrY2dieWxncnpqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5MDA0MzUyMywiZXhwIjoyMDA1NjE5NTIzfQ.1Ke79HmJjvzwAzWJiEq4DiGGsl3V1jBrolxtjYOgqDE"
supabase: Client = create_client(url, key)

# Bybit API
httpClient = requests.Session()
recv_window = str(5000)
url = "https://api.bybit.com"


# return executions (as a list)
def get_executions_list(csv_url):
    response = requests.get(csv_url)
    if response.status_code == 200:
        csv_data = response.text
        # Use the csv module to parse the CSV data into a list of dictionaries
        csv_reader = csv.DictReader(csv_data.splitlines())
        executions = list(csv_reader)
        return executions
    else:
        print("Failed to fetch the CSV data.")
        return []


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        user_id, user_account_name, user_key, user_secret = self.get_from_query()
        utid = supabase.table('users').select('uniqueTaskId').eq('id', user_id).execute().data[0]['uniqueTaskId']
        res = str(self.get_export_status(utid))
        response_data = {
            'message': res
        }

        if res == 'Processed':  # set utid to null, link to true
            supabase.table('users').update({'uniqueTaskId': None}).eq('id', user_id).execute()
            supabase.table('users').update({'link': True}).eq('id', user_id).execute()

        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    def get_from_query(self):
        from urllib.parse import urlparse, parse_qs
        query_components = parse_qs(urlparse(self.path).query)
        # need error handling here probably
        # will ask supabase for variables if not provided (except id)
        # this is for when user refreshed page and utid exists but link == false
        user_id = query_components.get('id', [''])[0]
        user_account_name = query_components.get('account_name', [supabase.table('users').select('bybit_account_name').eq('id', user_id).execute().data[0]['bybit_account_name']])[0]
        user_key = query_components.get('key', [supabase.table('users').select('bybit_api_key').eq('id', user_id).execute().data[0]['bybit_api_key']])[0]
        user_secret = query_components.get('secret', [supabase.table('users').select('bybit_api_secret').eq('id', user_id).execute().data[0]['bybit_api_secret']])[0]
        return user_id, user_account_name, user_key, user_secret
    # return user_id, user_account_name, user_key, user_secret

    def HTTP_Request(self, endPoint, method, payload, Info):
        global time_stamp
        user_id, user_account_name, user_key, user_secret = self.get_from_query()
        time_stamp = str(int(time.time() * 10 ** 3))
        signature = self.genSignature(payload)
        headers = {
            'X-BAPI-API-KEY': user_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-SIGN-TYPE': '2',
            'X-BAPI-TIMESTAMP': time_stamp,
            'X-BAPI-RECV-WINDOW': recv_window,
            'Content-Type': 'application/json'
        }
        # potential error handling place (unable to contact bybit api)
        if method == "POST":
            response = httpClient.request(method, url + endPoint, headers=headers, data=payload)
        else:
            response = httpClient.request(method, url + endPoint + "?" + payload, headers=headers)
        # print(response.text)
        # print(Info + " Elapsed Time : " + str(response.elapsed))
        return response.json()
    # return response

    def genSignature(self, payload):
        user_id, user_account_name, user_key, user_secret = self.get_from_query()
        param_str = str(time_stamp) + user_key + recv_window + payload
        hash = hmac.new(bytes(user_secret, "utf-8"), param_str.encode("utf-8"), hashlib.sha256)
        signature = hash.hexdigest()
        return signature
    # return signature for secret_key

    def get_export_status(self, uniqueTaskId):  # TODO
        global r
        endpoint = "/v5/execution/export-status"
        method = "GET"
        params = f"category=linear&uniqueTaskId={uniqueTaskId}"
        # print(params)
        r = self.HTTP_Request(endpoint, method, params, "Export")
        status = r['result']['status']
        s3url = r['result']['url']
        if s3url:
            # --> get csv
            # --> make list
            # --> add user_id, account_name, types
            # --> push to supabase
            # --> delete utid from supabase (done in main)
            # --> set link to true (done in main)
            return status
        else:
            return status
    # return s3url
