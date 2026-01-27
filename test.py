import requests

header = {
    "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3Njk0Nzg2NTQsInN1YiI6IjMifQ.VPbMq9HnxMw34aguo6aZA95hpHM0lvjhwClAMFobupE"
}

response = requests.get("http://127.0.0.1:8000/home/refresh", headers=header)
print(response.json())