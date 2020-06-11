import hvac
from dnacentersdk import DNACenterAPI

# Instantiate new Vault CLIENT
client = hvac.Client()

# Capture UNSEAL key when initializing your Vault Server
vault_unseal_key = '04fbe3bd94d1716d298a99830cbef8bd587521c4f5dafe5e08142f4b4f31bfc2'
# Capture the CLIENT TOKEN here, provided by your admin (in this case see POSTMAN Collection)
vault_client_token = 's.FBp8nWrsTJgePWHvp2W59Nmv'

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
