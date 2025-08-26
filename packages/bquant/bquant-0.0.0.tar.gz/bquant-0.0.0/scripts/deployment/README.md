# BQuant Deployment Scripts

Скрипты для развертывания, упаковки и публикации BQuant проекта.

## 🚧 В разработке

Этот модуль находится в стадии планирования и будет содержать:

## 🚀 Планируемые скрипты

### `build_package.py`
Сборка и упаковка BQuant для распространения.

**Планируемый функционал:**
- Сборка wheel и sdist пакетов
- Валидация метаданных пакета
- Проверка зависимостей
- Генерация README для PyPI
- Создание release notes

### `deploy_pypi.py`
Публикация пакета в PyPI.

**Планируемый функционал:**
- Автоматическая публикация в PyPI
- Управление версиями
- Тестирование на TestPyPI
- Rollback при ошибках
- Уведомления о релизах

### `setup_environment.py`
Настройка среды разработки и продакшена.

**Планируемый функционал:**
- Создание виртуальных окружений
- Установка зависимостей
- Настройка конфигурации
- Валидация окружения
- Миграция между версиями

### `run_ci_tests.py`
Выполнение CI/CD тестов.

**Планируемый функционал:**
- Запуск всех типов тестов
- Проверка code coverage
- Linting и code quality
- Security сканирование
- Performance benchmarks

### `generate_docs.py`
Генерация документации проекта.

**Планируемый функционал:**
- Автогенерация API документации
- Сборка Sphinx документации
- Создание GitHub Pages
- Обновление README файлов
- Генерация changelog

### `backup_data.py`
Резервное копирование критичных данных.

**Планируемый функционал:**
- Backup sample данных
- Архивирование результатов анализа
- Версионирование конфигураций
- Восстановление из backup
- Синхронизация с облаком

## 🛠️ Использование (планируемое)

```bash
# Сборка пакета
python build_package.py --version 0.0.0 --clean

# Публикация в PyPI
python deploy_pypi.py --version 0.0.0 --repository pypi

# Настройка окружения
python setup_environment.py --env production --python 3.9

# CI/CD тесты
python run_ci_tests.py --coverage --benchmarks

# Генерация документации
python generate_docs.py --output docs/ --format html

# Backup данных
python backup_data.py --target s3://bquant-backups/ --compress
```

## 🔧 Конфигурация

### Файлы конфигурации
- `deployment_config.yaml` - общие настройки развертывания
- `pypi_config.yaml` - настройки для PyPI публикации
- `ci_config.yaml` - конфигурация CI/CD

### Переменные окружения
- `PYPI_TOKEN` - токен для публикации в PyPI
- `GITHUB_TOKEN` - токен для GitHub интеграции
- `AWS_ACCESS_KEY` - для backup в S3
- `DEPLOYMENT_ENV` - среда развертывания (dev/staging/prod)

## 📋 Workflow развертывания

### 1. Pre-release
```bash
# Валидация кода
python run_ci_tests.py --full

# Обновление версии
python build_package.py --bump-version minor

# Генерация документации
python generate_docs.py --update-all
```

### 2. Release
```bash
# Сборка пакета
python build_package.py --version 1.1.0

# Тестирование на TestPyPI
python deploy_pypi.py --repository testpypi

# Публикация в PyPI
python deploy_pypi.py --repository pypi
```

### 3. Post-release
```bash
# Backup релиза
python backup_data.py --release 1.1.0

# Обновление environments
python setup_environment.py --update-all

# Мониторинг
python monitor_release.py --version 1.1.0
```

## 🧪 Тестирование развертывания

### Локальное тестирование
```bash
# Тест сборки
python build_package.py --dry-run

# Тест установки
pip install dist/bquant-0.0.0-py3-none-any.whl

# Тест функциональности
python -c "import bquant; print(bquant.__version__)"
```

### CI/CD Pipeline
- GitHub Actions для автоматического тестирования
- Автоматическая публикация релизов
- Интеграция с codecov
- Security сканирование с помощью bandit

## 📊 Мониторинг

### Метрики релизов
- Количество загрузок с PyPI
- Успешность установки
- Время развертывания
- Ошибки в production

### Алерты
- Неудачные развертывания
- Проблемы с зависимостями
- Security уязвимости
- Performance деградация

## 🔒 Безопасность

### Принципы
- Все секреты через переменные окружения
- Подписание релизов GPG ключом
- Валидация checksums
- Minimal permissions для токенов

### Аудит
- Логирование всех действий развертывания
- Версионирование конфигураций
- Rollback планы для каждого релиза

## 📖 Roadmap

1. **Фаза 1**: Базовые скрипты сборки и публикации
2. **Фаза 2**: CI/CD автоматизация
3. **Фаза 3**: Мониторинг и алертинг
4. **Фаза 4**: Multi-environment deployment

## 🚀 Контрибуция

Для добавления новых скриптов развертывания:
1. Следуйте принципам Infrastructure as Code
2. Используйте конфигурационные файлы
3. Добавляйте логирование и мониторинг
4. Тестируйте на staging среде
5. Документируйте rollback процедуры

## 🔗 См. также

- [BQuant Package Configuration](../../pyproject.toml)
- [GitHub Actions Workflows](../../.github/workflows/)
- [Release Process Documentation](../../docs/release_process.md)
- [Security Guidelines](../../docs/security.md)
