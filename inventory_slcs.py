import requests

session = requests.Session()
search_url = 'https://cmr.earthdata.nasa.gov/search/granules.json'
params = {
    'provider': 'ASF',
    'short_name': ['SENTINEL-1A_SLC', 'SENTINEL-1B_SLC'],
    'attribute[]': ['string,BEAM_MODE_TYPE,IW', 'string,BEAM_MODE_TYPE,EW'],
    'options[attribute][or]': 'true',
    'page_size': 2000,
}
headers = {}

with open('slcs.txt', 'w') as f:
    while True:
        response = session.get(search_url, params=params, headers=headers)
        response.raise_for_status()
        granules = response.json()['feed']['entry']
        for granule in granules:
            f.write(f'{granule["producer_granule_id"]}\n')
        if 'CMR-Search-After' not in response.headers:
            break
        headers['CMR-Search-After'] = response.headers['CMR-Search-After']
