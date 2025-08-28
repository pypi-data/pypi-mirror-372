# alxhttp
Some customization of aiohttp

Features:
- JSON logging
- middleware to add a unique request ID
- middleware to turn uncaught exceptions into JSON 500s
- a simple base server class pattern to follow

# Publish
uv build
twine upload dist/*
