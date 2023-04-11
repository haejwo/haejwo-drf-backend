import requests
import json, os
from dotenv import load_dotenv
load_dotenv()
# 요청에 필요한 데이터
data = {
  "businesses": [
    {
      "b_no": "2018187900",
      "start_dt": "20040702",
      "p_nm": "박건원",
    }
  ]
}

# API 엔드포인트 URL과 서비스 키
url = "https://api.odcloud.kr/api/nts-businessman/v1/validate"
service_key = os.getenv("DATA_KEY")

# POST 요청 보내기
response = requests.post(
    url,
    params={"serviceKey": service_key},
    data=json.dumps(data),
    headers={"Content-Type": "application/json", "Accept": "application/json"}
)

# 응답 결과 확인
if response.status_code == 200:
    result = response.json()
    print(result['data'][0].get('status'))
else:
    print(response.text)  # 에러 메시지 확인