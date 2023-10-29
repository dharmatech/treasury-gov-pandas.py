
import os
import time
import requests
import pandas as pd
# ----------------------------------------------------------------------
def download_records_after(url, date, page_size=10000):
    data = []

    page = 1
        
    url_params = f'?filter=record_date:gt:{date}&page[size]={page_size}'
    
    response = requests.get(url + url_params)

    if response.status_code == 200:

        result_json = response.json()

        data.extend(result_json['data'])

        while True:
            if result_json['links']['next'] is None:
                break
            else:
                
                response = requests.get(url + url_params + result_json['links']['next'])

                if response.status_code == 200:

                    result_json = response.json()

                    data.extend(result_json['data'])

                    page = page + 1

                    print(f'page {page} of {result_json["meta"]["total-pages"]}')

                    time.sleep(2)

                else:

                    print(f'status_code: {response.status_code}')

                    break

    else:
        print(f'status_code: {response.status_code}')

    return pd.DataFrame(data)
# ----------------------------------------------------------------------

# url = https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/dts/deposits_withdrawals_operating_cash

# path = 'deposits_withdrawals_operating_cash.pkl'

# path = 'data_act_compliance.pkl'
# url  = 'https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/debt/tror/data_act_compliance'
# start_date = '1900-01-01'
# page_size = 10000

def update_records(path, url, start_date='1900-01-01', page_size=10000):
    
    if os.path.isfile(path):
        print(f'Found {path}. Importing.')

        df = pd.read_pickle(path)

        # Get second most recent record_date
        recent_record_date = df['record_date'].unique()[-2]
        
        print(f'Second most recent record_date: recent_record_date {recent_record_date}')
        
        new_records = download_records_after(url, recent_record_date, page_size)
        
        df = df[df['record_date'] <= recent_record_date]

        df = pd.concat([df, new_records], ignore_index=True)

        df.to_pickle(path)
        
        return df

    else:
           
        recent_record_date = start_date

        print(f'Using recent_record_date: {recent_record_date}')
       
        df = download_records_after(url, recent_record_date, page_size)
       
        df.to_pickle(path)

        return df
