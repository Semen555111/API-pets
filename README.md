# Petstore API: pytest + Playwright

Ровно 7 независимых интеграционных тестов для [Swagger Petstore v3](https://petstore3.swagger.io/).
Контракт: [OpenAPI JSON](https://petstore3.swagger.io/api/v3/openapi.json).
Запросы выполняются через Playwright `APIRequestContext`; браузеры устанавливать не нужно.

## Запуск в Windows / PowerShell

В папке проекта уже создано окружение `.venv` и установлены зависимости.
Запустить тесты можно без активации окружения:

```powershell
.\.venv\Scripts\python.exe -m pytest -v
```

Или активировать окружение:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -v
```

Если PowerShell запрещает запуск `Activate.ps1`, используйте первый вариант.

Для установки проекта заново (Python 3.10+):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -v
```

## Сценарии

| Тест | Основной запрос | Проверка |
| --- | --- | --- |
| `test_create_pet` | `POST /pet` | 200, JSON и поля питомца; сохранение через GET |
| `test_get_pet_by_id` | `GET /pet/{id}` | 200, JSON и поля созданного питомца |
| `test_update_pet` | `PUT /pet` | 200, новое имя и статус; сохранение через GET |
| `test_find_pets_by_status` | `GET /pet/findByStatus` | 200, список с нужным статусом и созданным питомцем |
| `test_delete_pet` | `DELETE /pet/{id}` | 200; последующий GET возвращает 404 |
| `test_get_pet_with_invalid_id` | `GET /pet/not-an-integer` | 400 для нечислового ID |
| `test_find_pets_with_invalid_status` | `GET /pet/findByStatus` | 400 для неизвестного статуса |

Коды `200` для создания и удаления взяты из спецификации этого API.

## Организация проекта

- `tests/conftest.py`: фикстуры `api_context`, `pet_payload`, `created_pet`.
- `tests/test_pets.py`: тесты и общая проверка ответа с питомцем.
- `pytest.ini`: поиск тестов, строгая проверка конфигурации и маркер `api`.
- `requirements.txt`: зафиксированные версии зависимостей.
- `.gitignore`: исключения для окружения, кешей и отчётов.

Фикстура `playwright` предоставляется плагином `pytest-playwright`. Каждый тест
получает собственный HTTP-контекст. Тестовые питомцы имеют уникальные ID, имена и теги;
ID помещаются в безопасный целочисленный диапазон JavaScript, используемого Playwright.

Очистка регистрируется до создания питомца и выполняется в `finally`, в том числе при
падении проверки. Удаляются только собственные тестовые данные. При очистке допускаются
200 и 404, поскольку сценарий DELETE уже удаляет свою запись. Контекст запросов
закрывается после завершения теста и очистки данных. Тесты не зависят от порядка запуска.

## Настройки и отчёт

По умолчанию используется `https://petstore3.swagger.io/api/v3`, тайм-аут запроса — 15 секунд.
Для другого совместимого тестового стенда задайте переменную окружения:

```powershell
$env:PETSTORE_BASE_URL = "https://your-test-host.example/api/v3"
# Если стенд требует API key:
$env:PETSTORE_API_KEY = "your-test-api-key"
.\.venv\Scripts\python.exe -m pytest -v
```

Для запуска одного сценария и сохранения отчёта JUnit XML:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_pets.py::test_create_pet -v
.\.venv\Scripts\python.exe -m pytest -v --junitxml=reports/junit.xml
```

Тесты работают с настоящим публичным API и требуют интернета. Данные общего стенда
могут сбрасываться; ошибки сети и сервера будут видны как падения, без автоматических
повторов или пропуска проверок. Точный размер общего списка питомцев не фиксируется.
