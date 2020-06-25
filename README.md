## Securing your API authentication keys with Vault
![vault](imgs/vault-dnac.png)

## What is Vault?
Vault is a tool for securely accessing secrets. A **secret** is anything to which you want to tightly control access, such as API keys, passwords, or certificates. Vault provides a unified interface to any secret, while providing tight access control and recording a detailed audit log.

## Requirements
 1. Download and install [Vault](https://www.vaultproject.io/downloads).
 2. Download and install [Postman](https://www.postman.com/downloads/).
 3. Import the Postman collection and environment variable from the `Postman Collection` project folder.

 	⚠️ `Tests` are  written to the collection to automatically update your Postman environment variables.

## Getting Started
### Step 1: Start Vault
Once Vault is Installed, you need to start it. There are two options: one that runs Vault storage in memory and another that starts the server with a pre-existing config file.

![vault](imgs/vault-hcl.png)

#### **Option #1:** Start it up in `dev mode` by entering the following command in `Terminal`:
```Bash
vault server -dev
```
 ⚠️ This option runs Vault storage in memory; once the server is stopped your config and keys are lost.

 ⚠️ If this is the option you choose, make sure you capture the `UNSEAL key` and `ROOT TOKEN` that are provided.

#### **Option #2:** Start it up with a pre-existing config file by supplying the following `cmd` in `Terminal`:

```Bash
vault server -config config.hcl
```
 [An example Vault Config file found here](Vault-Config/config.hcl). Here's how it looks:

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

**storage.file.path** is the location where Vault creates a file system for storage. Set the `vault/data` value to whatever you like.

**ui:true** enables Vault's UI interface.

 ⚠️ Note that the Vault config file must be located in a folder to which you have read and write access permissions.

### Step 2: Initialize and Configure Vault
Open Postman and [import](https://learning.postman.com/docs/postman/collections/importing-and-exporting-data/)  `Vault.postman_collection` and `Vault-Env.postman_environment` from the Vault Collections folder, along with your environment variable.

 ⚠️  Here's where you can find the [Postman Collection](https://github.com/CiscoDevNet/vault/tree/master/Postman-Collection).

Assuming you chose to run vault using `Option #2` you will only need to initialize and configure Vault once on initial run.

In the Postman Vault Collection, execute the following commands:

1. `init vault` provides you with `UNSEAL Key` and `Root Token` values. Be sure to save these values someplace where you can retrieve them.
2. `unseal vault` unseals the vault before you can start accessing your secrets.
3. enable the [`KV secret engine`](https://www.vaultproject.io/docs/secrets/kv), which stores arbitrary secrets within the configured physical storage. In this case you are creating a new `mount` named `kv-v1`. Think of this as your path to secrets.

At this point you have everything you need to start storing API keys, authentication credentials, and tokens within your Vault instance.

### Step 3: Register the AppRole Application
You don't want to give our application `Root` access. Instead, you want to register an [AppRole](https://www.vaultproject.io/docs/auth/approle) to authenticate our app against your instance of Vault.

In the provided Postman Collection:

1. `Add AppRole` will setup a new AppRole authentication method within Vault.
2. `Add ACL Policy` Vault is driven by [policies](https://learn.hashicorp.com/vault/identity-access-management/iam-policies) to govern role-based access. In this case you are creating a policy to give access to the `kv-v1` secret engine mount you created previously.

This is what the ACL Policy `my-policy` looks like:

```shell
# Dev servers have version 1 of KV secrets engine mounted by default, so will
# need these paths to grant permissions:
path "kv-v1/devnet/dnac/*" {
  capabilities = ["create", "update","read"]
}
```
3.`Bind policy to role` does what is says in that it will bind `my-policy` to the `AppRole` you created and call it `my-role`.


### Step 4: Generate App Token
To generate a new `CLIENT TOKEN` you first need to fetch your `Role ID` and generate a new `Secret ID` based on the role.

In the provided Postman Collection:

1. `Get Role ID` fetches the `my-role` ID created above.
2. `Create Secret ID` uses the `my-role` ID you will generate a new `Secret ID`
3. `Fetch Client Token` generates a `client_token` for writing, reading, and updating secrets in the mount to which ACL granted permission; in this case `kv-v1/devnet/dnac/*` **Use this in you application to authenticate, Capture It!**


### Step 5: Create Secret
Now that you have all the pieces of the puzzle in place *(step 1-4 only need to be configured once)* you can now start storing secrets to be utilized by your application.

1. `Post KV Secret` uses the `client_token` to create a new secret. In this case we are using **Cisco DNA Center Sandbox** and writing the secret to the mount path `kv-v1/devnet/dnac/sb1`, with POST http://{{vault}}/v1/kv-v1/devnet/dnac/sb1 in Postman.

⚠️ You will need to remember your `mount paths` from the POST endpoint above in order to access your secrets.


## Automation in code
[The provided sample code will](vault.py):
1. Access Vault using the `HVAC` library, and fetch the secret.
2. Authenticate against Cisco DNA Center Always On Sandbox.
3. Pull a list of managed devices.

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

⚠️ Be sure to alter the `vault_unseal_key` and `vault_client_token` based on your instance of Vault.

```Python
# Instantiate new Vault client
client = hvac.Client()

# Capture the unseal key when initializing your Vault Server
vault_unseal_key = 'REPLACE_WITH_KEYS_VALUE_FROM_INIT_POST'

# Capture the client token provided by your admin (in this case, see the provided Postman Collection POST init vault request)
vault_client_token = 'REPLACE_WITH_ROOT_TOKEN_FROM_INIT_POST'

# Define your mount point and path where your secrets are saved
vault_mount_point = 'kv-v1'
vault_path = '/devnet/dnac/sb1'
```

## SUCCESS
You have now integrated your application with a centralized vault that holds some, if not all your API credentials and tokens in a secure fashion. Imagine automating a multi-domain environment where you have different API calls to different endpoints; juggling authentication tokens can be tedious and time consuming. Vault makes your life simple! Cool!
