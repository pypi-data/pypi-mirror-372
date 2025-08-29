# wiz

Wiz dynamic producer for Akeyless

The payload for this producer looks like:

```
{"clientId": "[YOUR_CLIENT_ID_HERE]", "clientSecret": "[YOUR_CLIENT_SECRET_HERE]"}
```

Call `clearskies_akeyless_custom_wiz.build_wiz_producer()` to initialize the create/rotate/revoke endpoints.  You can
optionally provide the `url` parameter which will add a prefix to the endpoints.  This can then be attached to a
[clearskies context](https://clearskies.info/docs/context/index.html) or an [endpoint group](https://clearskies.info/docs/endpoint-groups/endpoint-groups.html):

If used as a producer, it will use the client credentials to fetch and return a Wiz JWT.  It can also rotate the
client credentials you provide.

```
import clearskies
import clearskies_akeyless_custom_wiz

wsgi = clearskies.contexts.WsgiRef(
    clearskies_akeyless_custom_wiz.build_wiz_producer()
)
wsgi()
```

Which you can test directly using calls like:

```
curl 'http://localhost:8080/sync/create' -d '{"payload":"{\"clientId\":\"YOUR_CLIENT_ID_HERE\",\"clientSecret\":\"YOUR_CLIENT_SECRET_HERE\"}"}'

curl 'http://localhost:8080/sync/rotate' -d '{"payload":"{\"clientId\":\"YOUR_CLIENT_ID_HERE\",\"clientSecret\":\"YOUR_CLIENT_SECRET_HERE\"}"}'
```

**NOTE:** Akeyless doesn't store your payload as JSON, even when you put in a JSON payload.  Instead, it ends up as a stringified-json
(hence the escaped apostrophes in the above example commands).  This is normal, and normally invisible to you, unless you try to invoke the
endpoints yourself.
