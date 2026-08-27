import requests

def send_slack_message(webhook_url: str | None, message: str) -> None:
    slack_headers = {
        'Content-Type': 'application/json',
    }
    if not webhook_url:
        print("SLACK_WEBHOOK_URL not configured; Slack notification skipped")
        return
    response = requests.post(webhook_url, headers=slack_headers, json={"text": message}, timeout=10)
    response.raise_for_status()
