import requests
from user_agent import generate_user_agent as ua


def rest(username: str) -> dict:

    headers = {
        'user-agent': ua(),
        'x-csrftoken': 'tb9KuiockmVMmkquEDEiMkqAAplnqswt'
    }
    data = {'email_or_username': username}

    try:
        res = requests.post(
            'https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/',
            headers=headers, data=data
        ).json()
    except Exception as e:
        return {"status": False, "message": f"Request error: {e}"}

    if res.get('status') == 'ok':
        re = res.get('contact_point', 'Unknown')
        return {"status": True, "message": f"Send Email: {re}"}
    else:
        return {"status": False, "message": "An error occurred."}