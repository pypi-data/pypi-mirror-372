source <(vault kv get -format=json e-service/pypi/xethhung12/dev-deployment | jq -r ".data.data.token" | sed -E "s/(.*)/export TWINE_PASSWORD=\"\1\"/g")
export TWINE_USERNAME=__token__