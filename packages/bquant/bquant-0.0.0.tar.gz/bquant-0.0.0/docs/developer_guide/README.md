# Developer Guide - Руководство разработчика BQuant

## 📚 Обзор

Руководство разработчика содержит информацию для тех, кто хочет внести вклад в развитие BQuant или расширить его функциональность.

## 🗂️ Содержание

### 🏗️ [Architecture](architecture.md) - Архитектура
- Общая архитектура BQuant
- Принципы проектирования
- Модульная структура
- Паттерны проектирования

### 🔧 [Contributing](contributing.md) - Как внести вклад
- Настройка среды разработки
- Процесс разработки
- Code Style и стандарты
- Создание Pull Request

### 🧪 [Testing](testing.md) - Тестирование
- Структура тестов
- Написание unit тестов
- Интеграционные тесты
- Performance тесты

### ⚡ [Performance](performance.md) - Производительность
- Профилирование кода
- Оптимизация алгоритмов
- Кэширование
- Параллельная обработка

### 🔍 [Debugging](debugging.md) - Отладка
- Инструменты отладки
- Логирование
- Обработка ошибок
- Диагностика проблем

### 📦 [Packaging](packaging.md) - Упаковка
- Структура пакета
- Настройка pyproject.toml
- Создание дистрибутивов
- Публикация в PyPI

### 🔄 [CI/CD](ci_cd.md) - Непрерывная интеграция
- Настройка GitHub Actions
- Автоматические тесты
- Деплой
- Мониторинг качества

## 🎯 Целевая аудитория

### 👨‍💻 Разработчики
- **Новички** - Начните с Contributing и Testing
- **Опытные** - Изучите Architecture и Performance
- **Эксперты** - Погрузитесь в CI/CD и Packaging

### 🏢 Команды
- **Open Source** - Вклад в развитие проекта
- **Enterprise** - Адаптация под корпоративные нужды
- **Research** - Расширение для исследований

## 📋 Предварительные требования

### Технические навыки
- Python 3.8+
- Git и GitHub
- Тестирование (pytest)
- Документирование (Sphinx)

### Инструменты
```bash
# Основные инструменты
pip install pytest black flake8 mypy sphinx

# Дополнительные
pip install pre-commit tox coverage
```

## 🚀 Быстрый старт для разработчиков

### 1. Клонирование и настройка

```bash
# Клонируем репозиторий
git clone https://github.com/your-username/bquant.git
cd bquant

# Создаем виртуальное окружение
python -m venv venv_dev
source venv_dev/bin/activate  # Linux/Mac
# или
venv_dev\Scripts\activate     # Windows

# Устанавливаем в режиме разработки
pip install -e .[dev]
```

### 2. Запуск тестов

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=bquant

# Только unit тесты
pytest tests/unit/

# Только integration тесты
pytest tests/integration/
```

### 3. Проверка качества кода

```bash
# Форматирование
black bquant/

# Линтинг
flake8 bquant/

# Типизация
mypy bquant/

# Все проверки
pre-commit run --all-files
```

## 🏗️ Архитектурные принципы

### Модульность
- **Разделение ответственности** - Каждый модуль имеет четкую задачу
- **Слабая связанность** - Минимальные зависимости между модулями
- **Высокая когезия** - Связанные функции в одном модуле

### Расширяемость
- **Plugin архитектура** - Легкое добавление новых индикаторов
- **Factory паттерн** - Создание объектов через фабрики
- **Strategy паттерн** - Взаимозаменяемые алгоритмы

### Производительность
- **NumPy векторизация** - Использование NumPy для быстрых операций
- **Кэширование** - Сохранение результатов вычислений
- **Ленивые вычисления** - Вычисления только при необходимости

### Надежность
- **Обработка ошибок** - Graceful handling исключений
- **Валидация данных** - Проверка входных данных
- **Тестирование** - Покрытие тестами критических путей

## 🔧 Процесс разработки

### 1. Планирование
- **Issue creation** - Создание задачи на GitHub
- **Requirements** - Определение требований
- **Design** - Проектирование решения

### 2. Разработка
- **Branch creation** - Создание ветки для фичи
- **Implementation** - Реализация функциональности
- **Testing** - Написание и запуск тестов

### 3. Code Review
- **Self-review** - Проверка собственного кода
- **Peer review** - Код-ревью коллегами
- **CI checks** - Автоматические проверки

### 4. Integration
- **Merge** - Слияние в основную ветку
- **Deployment** - Развертывание
- **Monitoring** - Мониторинг

## 🧪 Тестирование

### Типы тестов

#### Unit Tests
```python
def test_macd_calculation():
    """Тест расчета MACD"""
    data = create_sample_data()
    analyzer = MACDZoneAnalyzer()
    result = analyzer.calculate_macd(data)
    
    assert len(result) == len(data)
    assert 'macd' in result.columns
    assert 'signal' in result.columns
```

#### Integration Tests
```python
def test_full_pipeline():
    """Тест полного пайплайна"""
    data = get_sample_data('tv_xauusd_1h')
    analyzer = MACDZoneAnalyzer()
    result = analyzer.analyze_complete(data)
    
    assert result.zones is not None
    assert result.statistics is not None
```

#### Performance Tests
```python
def test_performance():
    """Тест производительности"""
    data = create_large_dataset(10000)
    
    start_time = time.time()
    analyzer = MACDZoneAnalyzer()
    result = analyzer.analyze_complete(data)
    end_time = time.time()
    
    assert end_time - start_time < 10.0  # Должно выполняться за 10 секунд
```

### Покрытие тестами
```bash
# Генерация отчета о покрытии
pytest --cov=bquant --cov-report=html

# Минимальное покрытие
pytest --cov=bquant --cov-fail-under=80
```

## ⚡ Производительность

### Профилирование
```python
from bquant.core.performance import performance_monitor

@performance_monitor
def slow_function():
    """Функция с профилированием"""
    pass

# Или контекстный менеджер
with performance_context("operation_name"):
    # Код для профилирования
    pass
```

### Оптимизация
- **NumPy векторизация** - Избегайте циклов Python
- **Кэширование** - Сохраняйте результаты вычислений
- **Параллелизм** - Используйте multiprocessing для тяжелых задач

## 🔍 Отладка

### Логирование
```python
import logging
from bquant.core.logging_config import setup_logging

# Настройка логирования
setup_logging(level=logging.DEBUG)

# Использование в коде
logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### Обработка ошибок
```python
from bquant.core.exceptions import BQuantError, DataError

try:
    result = analyzer.analyze_complete(data)
except DataError as e:
    logger.error(f"Data error: {e}")
    # Обработка ошибки данных
except BQuantError as e:
    logger.error(f"BQuant error: {e}")
    # Обработка общей ошибки
```

## 📦 Упаковка

### Структура пакета
```
bquant/
├── __init__.py
├── core/
├── data/
├── indicators/
├── analysis/
├── visualization/
└── ...
```

### Настройка pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "bquant"
version = "0.0.0"
description = "Quantitative analysis library for financial data"
# ... остальные настройки
```

## 🔄 CI/CD

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e .[dev]
      - name: Run tests
        run: |
          pytest --cov=bquant
```

## 🤝 Вклад в проект

### Типы вкладов
- **Bug fixes** - Исправление ошибок
- **Feature requests** - Новые функции
- **Documentation** - Улучшение документации
- **Performance** - Оптимизация производительности
- **Testing** - Добавление тестов

### Процесс
1. **Fork** репозитория
2. **Create** ветку для фичи
3. **Implement** изменения
4. **Test** изменения
5. **Submit** Pull Request

## 🔗 Связанные разделы

- **[User Guide](../user_guide/)** - Руководство пользователя
- **[API Reference](../api/)** - Справочник API
- **[Tutorials](../tutorials/)** - Обучающие материалы
- **[Examples](../examples/)** - Примеры использования

## 📞 Поддержка разработчиков

### Каналы связи
- **GitHub Issues** - Для багов и проблем
- **GitHub Discussions** - Для вопросов и обсуждений
- **Pull Requests** - Для предложений изменений

### Ресурсы
- **[Contributing Guidelines](contributing.md)** - Подробное руководство
- **[Code of Conduct](../CODE_OF_CONDUCT.md)** - Правила поведения
- **[License](../LICENSE)** - Лицензия проекта

---

**Начать изучение:** [Architecture](architecture.md) 🏗️
