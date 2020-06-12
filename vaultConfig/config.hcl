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
