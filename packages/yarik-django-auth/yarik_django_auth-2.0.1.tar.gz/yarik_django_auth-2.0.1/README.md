# YARIK-django-auth

## Сборка пакета
```bash
python -m venv .venv
. ./.venv/bin/activate
pip install -r requirements.txt
python -m pip install build
python -m build
```

## Публикация в индексе
```bash
pip install twine
twine upload --repository-url http://<hostname>:<port> dist/*
```

## Установка пакета из индекса
```bash
pip install --index-url http://<hostname>:<port> yarik-django-auth --trusted-host <hostname>
```