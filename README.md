Proxy
=====

Use case: For development and testing.

```bash
make

curl "http://localhost:9923/_proxy"

_DATA='{"localhost:9923": "https://bbc.co.uk", "example.com": "http://example2.com"}' && \
curl \
  --request POST \
  --header "Content-Type: application/json" \
  --data "${_DATA}" \
  --url "http://localhost:9923/_proxy"

_DATA='{"github.com": "https://gitlab.com"}' && \
curl \
  --request PUT \
  --header "Content-Type: application/json" \
  --data "${_DATA}" \
  --url "http://localhost:9923/_proxy"

_DATA='{"example.com": ""}' && \
curl \
  --request DELETE \
  --header "Content-Type: application/json" \
  --data "${_DATA}" \
  --url "http://localhost:9923/_proxy"

curl "http://localhost:9923/_proxy"

curl "http://localhost:9923/"
open "http://localhost:9923/"

```