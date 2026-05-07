from google.cloud import secretmanager

def access_secret():
    client = secretmanager.SecretManagerServiceClient()

    name = "projects/605301150765/secrets/CLIENT-DB-DEV/versions/latest"
    response = client.access_secret_version(name=name)

    secret = response.payload.data.decode("UTF-8")
    print(secret)

access_secret()
