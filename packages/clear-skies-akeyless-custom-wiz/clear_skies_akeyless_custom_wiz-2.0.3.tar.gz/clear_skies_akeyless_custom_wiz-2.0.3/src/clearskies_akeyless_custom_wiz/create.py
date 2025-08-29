import clearskies

def create(clientId, clientSecret, requests):
    response = requests.post(
        'https://auth.app.wiz.io/oauth/token',
        data={
            "grant_type": "client_credentials",
            "audience": "wiz-api",
            "client_id": clientId,
            "client_secret": clientSecret,
        },
        headers={
            "content-type": "application/x-www-form-urlencoded",
        },
    )
    if response.status_code != 200:
        raise clearskies.exceptions.ClientError("Failed to fetch JWT from Wiz. Response from Wiz: " + response.content.decode('utf-8'))
    response_data = response.json()
    if not response_data.get("access_token"):
        raise clearskies.exceptions.ClientError("I received a 200 response when fetching a JWT from Wiz, but I couldn't find the access token :(")
    return {
        "access_token": response_data.get("access_token"),
    }
