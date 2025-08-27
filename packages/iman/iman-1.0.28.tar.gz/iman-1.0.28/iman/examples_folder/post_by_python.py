import requests
url = 'http://127.0.0.1:5000/test'
data = '{  "filename": "iman"}'
response = requests.post(url, data=data,headers={"Content-Type": "application/json"})
print(response.text)
print(response.json())