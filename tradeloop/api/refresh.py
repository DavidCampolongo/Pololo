import time
from http.server import BaseHTTPRequestHandler
from pybit.unified_trading import HTTP
import json
from supabase import create_client, Client


def get_executions(handler_instance):
    start_time = time.time()
    # Create Bybit API Session & Pull Parameters
    testnet = False
    api_key, secret_key = handler_instance.get_userapi_supabase()
    category = "linear"
    symbol = ""
    limit = 100
    cursor_executions = ''
    executions = []
    global merge_list
    global closed_trades
    global open_trades
    session = HTTP(testnet=testnet, api_key=api_key, api_secret=secret_key)
    # print("Connected to Bybit")

    # Bybit API Executions Pull
    while True:
        response = session.get_executions(
            category=category,
            symbol=symbol,
            limit=limit,
            # startTime=1600097860000,
            # endTime=1663169860000,
            cursor=cursor_executions)

        result = response['result']
        result_list = result['list']
        executions.extend(result_list)

        next_page = result.get('nextPageCursor')
        if next_page:
            cursor_executions = next_page
        else:
            break
    # print("Pulled Executions from Bybit API")
    end_time = time.time()
    execution_time = end_time - start_time
    return execution_time, executions


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        # Get the execution time and executions list using the get_executions function
        execution_time, executions = get_executions(self)

        # Convert the execution_time to a string
        execution_time_str = str(execution_time)

        # Write the execution_time_str and executions list to the response
        response_data = {
            'message': f'Execution Time:{execution_time_str} Executions:{executions}'
        }

        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return

    def get_id_from_query(self):
        from urllib.parse import urlparse, parse_qs
        query_components = parse_qs(urlparse(self.path).query)
        return query_components.get('id', [''])[0] or 'Guest'

    def get_userapi_supabase(self):
        user_id = self.get_id_from_query()
        # Connect to Supabase (service role)
        url = "https://xnqhlyvwofkcgbylgrzj.supabase.co"
        key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhucWhseXZ3b2ZrY2dieWxncnpqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTY5MDA0MzUyMywiZXhwIjoyMDA1NjE5NTIzfQ.1Ke79HmJjvzwAzWJiEq4DiGGsl3V1jBrolxtjYOgqDE"
        supabase: Client = create_client(url, key)
        # Using that, get the api_key & secret_key
        api_key = (supabase.table('users').select('bybit_api_key').eq('id', user_id).execute()).data[0]['bybit_api_key']
        secret_key = (supabase.table('users').select('bybit_api_secret').eq('id', user_id).execute()).data[0][
            'bybit_api_secret']
        return api_key, secret_key
