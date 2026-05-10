import requests

API_KEY = "dac36080-47f1-4d82-832f-066929c69eee"
BASE_URL = "https://airlabs.co/api/v9"

url = f"{BASE_URL}/ping"

params = {
    "api_key": API_KEY
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()
    print(data)
else:
    print("Error:", response.status_code)
    print(response.text)
