import requests, os
from dotenv import load_dotenv
load_dotenv()

service_key = os.getenv("KAKAO_REST_API_KEY")

url = "https://dapi.kakao.com/v2/local/search/address.json"
query = "유현로"
headers = {
    "Authorization": f"KakaoAK {service_key}"
}

params = {
    "query": query
}

response = requests.get(url, headers=headers, params=params)

data = response.json().get('documents')
if data:
    if len(data) == 1:
        address_data = data[0]
        road_data = address_data.get('road_address')
        road_address, zip_code = '', ''
        if road_data:
            road_address = road_data.get('address_name')
            zip_code = road_data.get('zone_no')
        old_address = address_data.get('address').get('address_name')
    else:
        result = []
        for i in data:
            result.append(i.get('address_name'))
        print(data)
else:
    print(data)
