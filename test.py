import requests

files = open('222.jpg', 'rb')
upload = {'image': files}
headers = {
    'Authorization': 'Bearer ',
}
res = requests.post('http://localhost:8000/accounts/image-upload/', headers=headers,files=upload)
print(res.text)