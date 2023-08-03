from http.server import BaseHTTPRequestHandler
import requests
import time
import hashlib
import hmac
import random
import json
from supabase import create_client, Client
from pybit.unified_trading import HTTP

# Bybit API
httpClient = requests.Session()
recv_window = str(5000)
url = "https://api.bybit.com"  # Testnet endpoint

# Connect to Supabase (service role)
supabase_url = "https://xnqhlyvwofkcgbylgrzj.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhucWhseXZ3b2ZrY2dieWxncnpqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5MDA0MzUyMywiZXhwIjoyMDA1NjE5NTIzfQ.1Ke79HmJjvzwAzWJiEq4DiGGsl3V1jBrolxtjYOgqDE"
supabase: Client = create_client(supabase_url, key)


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        api_check = self.check_api()
        if api_check == (1, 0, 0):
            r = str(self.request_export())
            response_data = {
                'message': r
            }
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return
        else:
            response_invalid = {
                'message': f'API check failed with: {api_check}'
            }
            self.wfile.write(json.dumps(response_invalid).encode('utf-8'))
            return

    def get_from_query(self):
        from urllib.parse import urlparse, parse_qs
        query_components = parse_qs(urlparse(self.path).query)
        # need error handling here probably
        user_id = query_components.get('id', [''])[0]
        user_account_name = query_components.get('account_name', [''])[0]
        user_key = query_components.get('key', [''])[0]
        user_secret = query_components.get('secret', [''])[0]
        return user_id, user_account_name, user_key, user_secret
    # return user_id

    def check_api(self):
        user_id, user_account_name, user_key, user_secret = self.get_from_query()
        try:
            session = HTTP(
                testnet=False,
                api_key=user_key,
                api_secret=user_secret,
            )
            res = session.get_api_key_information()
            access_type = res['result']['readOnly']  # 1 is Read-Only
            is_unified = res['result']['unified']  # 0 is Normal Account
            is_uta = res['result']['uta']  # 0 is Normal Account
            return access_type, is_unified, is_uta
        except Exception as e:
            return e

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

    def request_export(self):
        endpoint = "/v5/execution/export"
        method = "POST"
        params = json.dumps({"category": "linear", "uniqueTaskId": str(random.randint(100000, 999999))})
        # Check if API is read only, if not return custom error
        r = self.HTTP_Request(endpoint, method, params, "Export")
        if r["retCode"] == 0:
            utid = r['result']['uniqueTaskId']
            user_id, user_account_name, user_key, user_secret = self.get_from_query()
            # Write query components to supabase after successfully requesting export
            supabase.table('users').update({'bybit_account_name': user_account_name, 'bybit_api_key': user_key, 'bybit_api_secret': user_secret, 'uniqueTaskId': utid}).eq('id', user_id).execute()
            return 'success'
        elif r["retCode"] == 10000:
            return '10000 - Server Timeout'
        elif r["retCode"] == 10001:
            return '10001 - Request parameter error'
        elif r["retCode"] == 10002:
            return '10002 - The request time exceeds the time window range.'
        elif r["retCode"] == 10003:
            return '10003 - API key is invalid'
        elif r["retCode"] == 10004:
            return '10004 - Error sign, please check your signature generation algorithm'
        elif r["retCode"] == 10005:
            return '10005 - Permission denied, please check your API key permissions'
        elif r["retCode"] == 10006:
            return '10006 - Too many visits. Exceeded the API Rate Limit'
        elif r["retCode"] == 10009:
            return "1009 - IP has been banned"
        elif r["retCode"] == 10010:
            return "10010 - Unmatched IP, please check your API key's bound IP addresses"
        elif r["retCode"] == 10016:
            return "10016 - Server Error"
        elif r["retCode"] == 10017:
            return "10017 - Route not found"
        elif r["retCode"] == 10018:
            return "10018 - Exceeded the IP Rate Limit"
        else:
            return f'unknown error ({r["retCode"]})'
    # return utid (unique task id) & write to supabase db | or not
