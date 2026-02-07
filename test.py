import requests

header = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NzA0MjY3NDcsInN1YiI6IjMifQ.nsgiUIDK6lDOpnf0JlI37Re1GyHHZtmxh8KrrCy4PNA"
}

response = requests.get("http://127.0.0.1:8000/home/refresh", headers=header)
print(response.json())