import requests

url = 'http://localhost:8000/movequotes/'

data = {
    'title': 'My Trip',
    'content': 'I went on a trip to the beach.',
    'date': '2023-03-08',
    'time': '10:00 AM',
    'status': 'MATCHING',
    'has_review': False,
    'size_type': 'SMALL',
    'packing_type': 'PACKING',
    'customer_support': True,
    'start_info': {},
    'end_info': {},
    'luggage_info': {}
}

image_file_descriptor = open('222.jpg', 'rb')
files = {'image': image_file_descriptor}
headers = {
    'Authorization': '',
}

response = requests.post(url, data=data, headers=headers, files=files)
print(response.text)
if response.status_code == 200:
    print('Success!')
else:
    print('Error!')