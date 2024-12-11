Proxy
=====

Use case: For development and testing.

```bash
make

_DATA='{"localhost:9100": "bbc.co.uk", "example.com": "example2.com"}' \
curl \
  --request POST \
  --header "Content-Type: application/json" \
  --data "${_DATA}" \
  --url "http://localhost:9100/_proxy"

_DATA='{"github.com": "gitlab.com"}' \
curl \
  --request PUT \
  --header "Content-Type: application/json" \
  --data "${_DATA}" \
  --url "http://localhost:9100/_proxy"

_DATA='{"example.com": ""}' \
curl \
  --request DELETE \
  --header "Content-Type: application/json" \
  --data "${_DATA}" \
  --url "http://localhost:9100/_proxy"

curl "http://localhost:9100/_proxy"

curl "http://localhost:9100/"
```