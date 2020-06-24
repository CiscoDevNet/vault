import hvac
import os
from dnacentersdk import DNACenterAPI

# Instantiate new Vault CLIENT
client = hvac.Client()
print(os.environ)
# Capture UNSEAL key we set in Env. Variable
vault_unseal_key = os.environ['UNSEAL_KEY']
print(vault_unseal_key)
# Capture the CLIENT TOKEN we set in Env. Variable
vault_client_token = os.environ['CLIENT_TOKEN']
print(vault_client_token)
# Define your MOUNT POINT and PATH where your secrets are saved
vault_mount_point = 'kv-v1'
vault_path = '/devnet/dnac/sb1'


def vault_auth():
    """
    This function will check if the vault is sealed, unseal it and authenticate against vault
    """
    # Check if vault is sealed
    if client.sys.is_sealed() == True:
        # if the vault is SEALED, UNSEAL IT using the unseal_key
        unseal_response = client.sys.submit_unseal_key(vault_unseal_key)

    # [Uncomment line below only if you want to generate a new API token for the application your ROOT admin registered]
    # Keep in mind you need Application Role ID and Secret ID
    # client_data = client.auth_approle(vault_role_id, vault_secret_id)

    # Authenticate against the VAULT using the new CLIENT TOKEN
    client.token = vault_client_token


def vault_r_secret(mount, path):
    """
    This function will read secret from the MOUNT you've created in VAULT and return the secret
    """
    read_secret_result = client.secrets.kv.v1.read_secret(path=vault_path, mount_point=vault_mount_point)
    return read_secret_result


def get_dnac_token(env_creds):
    """
    This function will Authenticate against Cisco DNA Center server and print out a list of all managed devices
    """
    dnac = DNACenterAPI(username=env_creds['data']['username'],
                        password=env_creds['data']['password'],
                        base_url=env_creds['data']['url'])
    print("DNAC API Authenticated ...")
    print("Gathering Device Info ... \n")
    devices = dnac.devices.get_device_list()
    for device in devices.response:
        print("Device Management IP {} for {} ".format(device.managementIpAddress, device.hostname))


if __name__ == '__main__':
    vault_auth()
    env_creds = vault_r_secret(vault_mount_point, vault_path)
    get_dnac_token(env_creds)
