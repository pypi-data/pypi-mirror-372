. .env
rm dist/*
rm -rf *.egg-info
uv build
echo $UV_PUBLISH_USERNAME
echo $UV_PUBLISH_URL
#uv publish -u $UV_PUBLISH_USERNAME -p $UV_PUBLISH_PASSWORD --publish-url $UV_PUBLISH_URL
uv publish -t $UV_PUBLISH_TOKEN