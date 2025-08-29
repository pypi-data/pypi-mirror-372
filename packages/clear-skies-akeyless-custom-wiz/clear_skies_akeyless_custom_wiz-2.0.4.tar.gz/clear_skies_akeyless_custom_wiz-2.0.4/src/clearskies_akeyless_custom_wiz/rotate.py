import json
import base64
import clearskies
from clearskies_akeyless_custom_wiz.create import create

def rotate(clientId, clientSecret, requests):
    jwt = create(clientId, clientSecret, requests)["access_token"]
    raw_subclaims = jwt.split(".")[1]
    subclaims = json.loads(base64.b64decode(raw_subclaims + '==').decode('utf-8').strip())
    if "dc" not in subclaims:
        raise clearskies.exceptions.ClientError("For some strange reason the JWT returned by Wiz didn't contain a 'dc' claim. :shrug:")
    dc = subclaims["dc"]

    gql_query = """
    mutation RotateServiceAccountSecret($input: String!) {
      rotateServiceAccountSecret(ID: $input) {
        serviceAccount {
          ...ServiceAccount
          clientSecret
        }
      }
    } fragment ServiceAccount on ServiceAccount {
      id enabled name clientId scopes lastRotatedAt expiresAt description integration
      { id name typeConfiguration { type iconUrl } }
    }
    """

    rotate_response = requests.post(
        f"https://api.{dc}.app.wiz.io/graphql",
        json={
            "query": gql_query,
            "variables": { "input": clientId },
        },
        headers={
            "content-type": "application/json",
            "Authorization": f"Bearer ${jwt}",
        }
    )

    if rotate_response.status_code != 200:
        raise clearskies.exceptions.ClientError("Rotate request rejected by Wiz.  Response: " + rotate_response.content.decode('utf-8'))
    new_credentials = rotate_response.json().get("data", {}).get("rotateServiceAccountSecret", {}).get("serviceAccount", {})
    if not new_credentials:
        raise clearskies.exceptions.ClientError("Huh, I did not understand the response from Wiz after my rotate request.  The response body did not have the expected shape :(")
    if not new_credentials.get("clientId"):
        raise clearskies.exceptions.ClientError("clientId missing in response from rotate operation")
    if not new_credentials.get("clientSecret"):
        raise clearskies.exceptions.ClientError("clientSecret missing in response from rotate operation")

    return {
        "clientId": new_credentials["clientId"],
        "clientSecret": new_credentials["clientSecret"],
    }
