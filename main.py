from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import cloudscraper
import json
from time import sleep
import random
from fake_useragent import UserAgent

app = FastAPI()

# Add CORS middleware
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    try:
        login_response = scraper.post("https://xrpspin.com/api.php?act=login", json=login_payload)
        # login_data = login_response.json() if login_response.text else {}

        if login_response.status_code == 200:
            sleep(random.uniform(2, 3))
            withdraw_response = scraper.post("https://xrpspin.com/api.php?act=withdrawXrp", json=withdraw_payload)

            try:
                withdraw_data = withdraw_response.json()
                return withdraw_data["parameters"][:-1]
            except (json.JSONDecodeError, KeyError, TypeError):
                return withdraw_data if 'withdraw_data' in locals() else "Invalid response"
        else:
            return "Login failed"

    except Exception as e:
        return f"Error: {str(e)}"

@app.post("/send")
def send_request(data: AccountRequest):
    result = process_account(data.email, data.tag)
    return result
@app.get("/author")
def read_root():
    return {"link": "https://ihatech.vercel.app"}
