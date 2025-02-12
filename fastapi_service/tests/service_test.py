import requests
import json
import uuid
import random
import time

# API endpoint and authorization details
url = "http://localhost:8000/background/enqueue"
# Replace with your actual bearer token and any cookies if required.
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0VXNlcjFAZ21haWwuY29tIiwiZXhwIjoxNzM2NjgyNjcxfQ.50nJqWCCOQ0uA-EE2X7LgNhDj-jKyEezo1oO6pkXqC0',
    'Cookie': 'refresh_token=YOUR_REFRESH_TOKEN_HERE'
}

def generate_payload():
    # Generate a new random chain_id
    chain_id = str(uuid.uuid4())
    # Generate a random file name for the "file_path" argument (e.g., chain3-out_<random>.md)
    random_int = random.randint(1, 100000)
    file_name = f"chain3-out_{random_int}.md"

    # Build the payload based on the given data format.
    payload = {
        "chain": {
            "chain_id": chain_id,
            "chain": [
                {
                    "from_agent": "user",
                    "to_agent": "content_writer",
                    "message": "write a moderately detailed report on ai systems, save it as .md format",
                    "args": [
                        {
                            "arg_name": "topic",
                            "arg_value": "write a moderately detailed report on ai systems, save it as .md format aimed at a general audience, format it in .md format.",
                            "is_static": True
                        }
                    ],
                    "chain_id": chain_id
                },
                {
                    "from_agent": "content_writer",
                    "to_agent": "write_file",
                    "message": "Write the content to new.txt",
                    "args": [
                        {
                            "arg_name": "file_path",
                            "arg_value": file_name,
                            "is_static": True
                        },
                        {
                            "arg_name": "data",
                            "arg_value": "None",
                            "is_static": False
                        }
                    ],
                    "chain_id": chain_id
                }
            ],
            "message": "New chain incoming",
            "cron": {
                "minute": "0",
                "hour": "*/1",
                "day_of_week": "*",
                "day_of_month": "*",
                "month_of_year": "*"
            }
        }
    }
    return payload

def main():
    num_requests = 500

    for i in range(num_requests):
        payload = generate_payload()
        # Convert payload dict to JSON
        payload_json = json.dumps(payload)

        try:
            time.sleep(2)
            response = requests.post(url, headers=headers, data=payload_json)
            if response.ok:
                print(f"Request {i+1}: SUCCESS - Status Code: {response.status_code}")
            else:
                print(f"Request {i+1}: FAILED - Status Code: {response.status_code} - Response: {response.text}")
        except Exception as e:
            print(f"Request {i+1}: Exception occurred - {e}")
        
        # Optionally, add a small delay between requests
        time.sleep(0.1)

if __name__ == "__main__":
    main()