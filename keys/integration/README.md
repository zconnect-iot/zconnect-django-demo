From google docs:

```
psql "sslmode=verify-ca sslrootcert=server-ca.pem \
    sslcert=client-cert.pem sslkey=client-key.pem \
    hostaddr=35.189.124.92 \
    port=5432 \
    user=postgres dbname=postgres"
```
