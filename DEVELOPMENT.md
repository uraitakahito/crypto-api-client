# Development

## Debugging with Visual Studio Code

Sample debug configurations are defined in [launch.json.sample](../.vscode/launch.json.sample). Run them from the `Run and Debug` panel.

## Getting the Development Dockerfile

```console
% curl -L -O https://raw.githubusercontent.com/uraitakahito/hello_python_uv/refs/tags/1.2.1/Dockerfile.dev
% curl -L -O https://raw.githubusercontent.com/uraitakahito/hello_python_uv/refs/tags/1.2.1/docker-entrypoint.sh
% chmod 755 docker-entrypoint.sh
```

Detailed instructions for setting up the development environment are documented as comments within the downloaded Dockerfile.

## Running Tests

```bash
uv run pytest tests/ -v
```
