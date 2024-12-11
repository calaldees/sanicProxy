* https://github.com/jupyterhub/configurable-http-proxy
* https://github.com/corridor/configurable-http-proxy


```bash
docker run --rm \
    --publish 8000:8000 \
    --publish 8001:8001 \
    --add-host host.docker.internal:host-gateway \
    --name configurable-http-proxy \
    bitnami/configurable-http-proxy:latest \
        --api-ip 0.0.0.0 \
        --host-routing \
&& true

curl http://localhost:8001/api/routes

curl \
    --request POST \
    --url 'http://localhost:8001/api/routes/test.com' \
    --data '{"target": "http://host.docker.internal:8002"}' \
&& true

curl \
    --request GET \
    --url 'http://localhost:8000/' \
    --header 'Host: test.com' \
&& true

```

https://github.com/jupyterhub/configurable-http-proxy?tab=readme-ov-file#host-based-routing
```json
{
  "/example.com": "https://localhost:1234",
  "/otherdomain.biz": "http://10.0.1.4:5555",
}
```


https://herald.musicradio.com/api/athena/services/epg-id:25/
```
curl \
    --request GET \
    --url 'http://localhost:8000/api/athena/services/epg-id:25/' \
    --header 'Host: herald' \
&& true

curl \
    --request GET \
    --url 'http://localhost:8000/static/proxy-frontend.html' \
&& true

```

---

```bash
curl -X GET  --url http://localhost:9100/_proxy
curl -X POST --url http://localhost:9100/_proxy -d '{"host": "test.com", "target":"test.com"}'
```
