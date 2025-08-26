# BQuant Scripts

Скрипты автоматизации для различных задач BQuant проекта.

## 📁 Структура

### `analysis/`
Скрипты для анализа данных:
- `run_macd_analysis.py` - Запуск MACD анализа
- `test_hypotheses.py` - Тестирование статистических гипотез
- `batch_analysis.py` - Пакетный анализ множества инструментов

### `data/`
Скрипты для работы с данными:
- `extract_samples.py` - Извлечение sample данных из исходных файлов

### `data_processing/`
Скрипты для обработки данных:
- Placeholder для будущих скриптов обработки данных
- Планируется: очистка данных, валидация, конвертация форматов

### `deployment/`
Скрипты для развертывания:
- Placeholder для будущих скриптов развертывания
- Планируется: упаковка, публикация, CI/CD

## 🚀 Использование

### Анализ данных
```bash
# MACD анализ
python scripts/analysis/run_macd_analysis.py XAUUSD 1h

# Тестирование гипотез
python scripts/analysis/test_hypotheses.py XAUUSD 1h

# Пакетный анализ
python scripts/analysis/batch_analysis.py --symbols XAUUSD,EURUSD --timeframe 1h
```

### Работа с данными
```bash
# Извлечение sample данных
python scripts/data/extract_samples.py --extract-all
python scripts/data/extract_samples.py --dataset tv_xauusd_1h
```

## 📋 Требования

- Python 3.8+
- Активированное виртуальное окружение BQuant
- Установленные зависимости BQuant (`pip install -e .`)

## 🛠️ Разработка

При создании новых скриптов следуйте принципам:
- CLI интерфейс с argparse
- Логирование через BQuant logger
- Обработка ошибок
- Документация и примеры использования
- Тестирование функциональности

## 📖 Документация

Подробная документация для каждого скрипта находится в соответствующих папках.
