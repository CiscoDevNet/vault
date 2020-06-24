## Securing your API authentication keys with Vault
![vault](imgs/vault-dnac.png)

## What is Vault?
Vault is a tool for securely accessing secrets. A secret is anything that you want to tightly control access to, such as API keys, passwords, or certificates. Vault provides a unified interface to any secret, while providing tight access control and recording a detailed audit log.


## Requirements
 1. Download and Install [Vault](https://www.vaultproject.io/downloads)
 2. Download and Install [postman](https://www.postman.com/downloads/)
 3. Import the Postman collection and environment variable from project folder `Postman Collection`
 
 	⚠️ `Tests` are  written part of the collection to auto-update your Postman environment variables.
 
## Getting Started
#### Step 1: Start Vault
Once Vault is Installed, you first need to start it up. There are two options:

![vault](imgs/vault-hcl.png)

###### **Option #1:** Start it up in `dev mode` by supplying the following cmd in `Terminal`
```Bash
vault server -dev
```
 ⚠️ This option runs Vault storage in memory and hence once the server is stopped your config and keys are lost.
 
 ⚠️ If this is the option you choose, make sure you capture the `UNSEAL key` and `ROOT TOKEN` that's provided.
  
###### **Option #2:** Start it up with a pre-existing config. by supplying the following cmd in `Terminal`
 
```Bash
vault server -config config.hcl 
```
 ⚠️ [Vault Config file found here](Vault-Config/config.hcl) 

`config.hcl` this is what vault look for on startup. Here what it looks like:

```JSON
	{
	"listener": [{
	"tcp": {
	"address" : "0.0.0.0:8200",
	"tls_disable" : 1
	}
	}],
	"api_addr": "http://0.0.0.0:8200",
	"storage": {
	    "file": {
	    "path" : "vault/data"
	    }
	 },
	"max_lease_ttl": "10h",
	"default_lease_ttl": "10h",
	"ui":true
	}
```
**address** is the *vault* server address, that's the same address we will use to access the UI in a browser.

**storage.file.path** is the location where *vault* is going to create a file system for storage. Set to `vault/data` change value as you see fit.

**ui:true** enables vault's UI interface.


### Step 2: Initialize and Configure Vault
Locate the provided Postman Collection folder, [import](https://learning.postman.com/docs/postman/collections/importing-and-exporting-data/) the `Vault.postman_collection` & `Vault-Env.postman_environment` into Postman and env variable and start initializing vault using its APIs.

 ⚠️  [Postman Collection found here](Postman-Collection) 

Assuming you chose to run vault using `Option #2` you will need to Initialize vault only once on initial run.

In Postman in the Vault Collection, execute the following request:

⚠️ You only need to do the following once, upon initial setup of Vault.

1. `init vault` this will provide you with the `UNSEAL Key` and `Root Token`. Save these values.
2. `unseal vault` this will do what it says, unseal the vault before you can start accessing your secrets.
3. `enable KV secret engine` [The KV secret engine](https://www.vaultproject.io/docs/secrets/kv) is used to store arbitrary secrets within the configured physical storage. In this case we are creating a new `mount` named `kv-v1`. Think of this as your path to secrets.

At this point you have everything you need to start storing API keys, Authentication, and Tokens within your Vault instance.

### Step 3: Register Application
We don't want to give our application `Root` access, we want to register an [AppRole](https://www.vaultproject.io/docs/auth/approle) to authenticate our app against our instance of Vault. 

In the provided Postman Collection:

1. `Add AppRole` this will setup a new AppRole authentication method within Vault.
2. `Add ACL Policy` Vault is driven by [policies](https://learn.hashicorp.com/vault/identity-access-management/iam-policies) to govern role based access. In this case we are creating a policy to give access to KV secret engine mount we created previously `kv-v1`. 

This is what the ACL Policy `my-policy` looks like:

```shell
# Dev servers have version 1 of KV secrets engine mounted by default, so will
# need these paths to grant permissions:
path "kv-v1/devnet/dnac/*" {
  capabilities = ["create", "update","read"]
}
```
3.`Bind policy to role` this will do what is says. It will bind `my-policy` to `AppRole` we've created and call it `my-role`  


### Step 4: Generate App Token
To generate a new `CLIENT TOKEN` we will first need to Fetch our `Role ID` and generate a new `Secret ID` based on the role.

In the provided Postman Collection:

1. `Get Role ID` fetches `my-role` ID created above. 
2. `Create Secret ID` using the `my-role` ID you will generate a new `Secret ID` 
3. `Fetch Client Token` this will generate a `client_token` for us to use to Create, Read, and Update Secrets in the mount our ACL granted permission to in this case `kv-v1/devnet/dnac/*` **Use this in you application to authenticate, Capture It!**


### Step 5: Create Secret 
Now that we have all the pieces of the puzzle in place *(step 1-4 we only need to configure once)* we can now start storing secrets to be utilized by our application.

1. `Post KV Secret` using the `client_token`, we will create a new secret. In this case we are using **Cisco DNA Center Sandbox** and writing the secret to the mount path `kv-v1/devnet/dnac/sb1`, with POST http://{{vault}}/v1/kv-v1/devnet/dnac/sb1 in Postman.

⚠️ You will need to remember your `mount paths` from the POST endpoint above in order to access your secrets.


## Automation in code
[Provided sample code will](vault.py)
1. Access Vault using `HVAC` library, and fetch the secret.
2. Authenticate against Cisco DNA Center Always On Sandbox.
3. Pull a list of managed Devices.

##### Prerequisites 

```shell
python3 -m venv venv
```
```shell
source venv/bin/activate
```
```shell
pip3 install -r requirements.txt
```

⚠️ Put the `UNSEAL KEY` and `CLIENT TOKEN` into an environment variable 

**Terminal:** 

```Bash
export CLIENT_TOKEN=<PLACE_YOUR_CLIENT_TOKEN_HERE>
export UNSEAL_KEY=<PLACE_YOUR_UNSEAL_KEY_HERE>
```

**[Python](vault.py):** 

```Python
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
```

## SUCCESS
You have now integrated your application with a centralized vault that holds some, if not all your API Credentials and Tokens in a secure fashion. Imagine automating a multi-domain environment where you have different API calls to different endpoints, juggling Auth Token can be tedious and time consuming. Vault makes your life simple! Cool!


 
