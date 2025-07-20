from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cloudscraper
import json
from time import sleep
import random
from fake_useragent import UserAgent

app = FastAPI()

class AccountRequest(BaseModel):
    email: str
    tag: str

def process_account(username, tag):
    ua = UserAgent()

    tag = str(tag).strip()
    if not tag.isdigit():
        return "Invalid tag format"

    login_payload = {
        "username": username,
        "password": "Matako"
    }

    withdraw_payload = {
        "confirm": 0,
        "payout_value": 0.000025,
        "password": "Matako",
        "xrpAddr": "rHcXrn8joXL2Qe7BaMnhB5VRuj1XKEmUW6",
        "distTag": tag
    }

    scraper = cloudscraper.create_scraper()
    scraper.headers.update({
        'User-Agent': ua.random,
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    })

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            login_response = scraper.post("https://xrpspin.com/api.php?act=login", json=login_payload)
            # login_data = login_response.json() if login_response.text else {}

            if login_response.status_code == 200:
                sleep(random.uniform(2, 3))
                withdraw_response = scraper.post("https://xrpspin.com/api.php?act=withdrawXrp", json=withdraw_payload)
                print(withdraw_response.text)

                try:
                    withdraw_data = withdraw_response.json()
                    if withdraw_data.get('parameters'):
                        response_message = withdraw_data['parameters'][1]
                    else:
                        response_message = withdraw_data.get('message', 'Unknown response')

                    if "Incorrect destination tag" in response_message:
                        retry_count += 1
                        if retry_count < max_retries:
                            sleep(random.uniform(3, 5))
                            continue

                    return response_message

                except json.JSONDecodeError:
                    return "Invalid response"
            else:
                return "Login failed"

        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                sleep(random.uniform(2, 3))
            else:
                return f"Error: {str(e)}"

@app.post("/send")
def send_request(data: AccountRequest):
    result = process_account(data.email, data.tag)
    if "success" in result.lower():
        return {"status": "success", "message": result}
    else:
        raise HTTPException(status_code=400, detail=result)
