import http.client

conn = http.client.HTTPSConnection("api.tosspayments.com")

payload = "{\"amount\":15000,\"orderId\":\"jySnp0l-iAWOmqG4_1LYv\",\"orderName\":\"토스 티셔츠 외 2건\",\"customerName\":\"박토스\",\"bank\":\"20\",\"cashReceipt\":{\"type\":\"소득공제\",\"registrationNumber\":\"01011111111\"}}"

headers = {
    'Authorization': "Basic test_ck_k6bJXmgo28eEod9R91Y8LAnGKWx4",
    'Content-Type': "application/json"
    }

conn.request("POST", "/v1/virtual-accounts", payload, headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))