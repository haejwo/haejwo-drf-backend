import requests

files = open('222.jpg', 'rb')
upload = {'image': files}

res = requests.post('http://localhost:8000/accounts/image-upload/', files=upload)
print(res.text)