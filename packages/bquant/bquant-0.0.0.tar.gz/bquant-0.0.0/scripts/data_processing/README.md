# BQuant Data Processing Scripts

Скрипты для обработки, очистки и конвертации финансовых данных.

## 🚧 В разработке

Этот модуль находится в стадии планирования и будет содержать:

## 📊 Планируемые скрипты

### `clean_data.py`
Очистка финансовых данных от выбросов и ошибок.

**Планируемый функционал:**
- Удаление дубликатов
- Обнаружение и коррекция выбросов
- Заполнение пропущенных значений
- Валидация OHLCV логики
- Нормализация временных меток

### `convert_formats.py`
Конвертация между различными форматами данных.

**Планируемый функционал:**
- CSV ↔ JSON ↔ Parquet ↔ HDF5
- MetaTrader ↔ TradingView ↔ Yahoo Finance
- Унификация схем данных
- Сжатие и оптимизация размера

### `validate_data.py`
Комплексная валидация качества данных.

**Планируемый функционал:**
- Проверка целостности OHLCV
- Валидация временных рядов
- Обнаружение gaps и inconsistencies
- Генерация отчетов о качестве данных

### `resample_data.py`
Ресэмплинг данных на различные таймфреймы.

**Планируемый функционал:**
- M1 → M5, M15, H1, H4, D1
- Агрегация volume и других метрик
- Сохранение статистических свойств
- Batch обработка множества инструментов

### `enrich_data.py`
Обогащение данных дополнительными индикаторами.

**Планируемый функционал:**
- Расчет технических индикаторов
- Добавление фундаментальных данных
- Создание derived features
- Feature engineering для ML

## 🛠️ Использование (планируемое)

```bash
# Очистка данных
python clean_data.py --input raw_data.csv --output clean_data.csv

# Конвертация форматов
python convert_formats.py --input data.csv --output data.parquet --format parquet

# Валидация
python validate_data.py --input data.csv --report validation_report.html

# Ресэмплинг
python resample_data.py --input M1_data.csv --timeframe H1 --output H1_data.csv

# Обогащение
python enrich_data.py --input ohlcv.csv --indicators RSI,MACD,BB --output enriched.csv
```

## 📋 Требования

- Python 3.8+
- pandas >= 1.3.0
- numpy >= 1.21.0
- pyarrow (для Parquet)
- tables (для HDF5)
- BQuant core modules

## 🔗 Интеграция с BQuant

Все скрипты будут интегрированы с:
- `bquant.data.loader` - для загрузки данных
- `bquant.data.processor` - для базовой обработки
- `bquant.data.validator` - для валидации
- `bquant.indicators` - для расчета индикаторов

## 🧪 Тестирование

Планируемые тесты:
- Unit тесты для каждого скрипта
- Integration тесты с sample data
- Performance тесты на больших объемах
- Качество выходных данных

## 📖 Roadmap

1. **Фаза 1**: Базовые скрипты очистки и валидации
2. **Фаза 2**: Конвертация форматов и ресэмплинг
3. **Фаза 3**: Обогащение и feature engineering
4. **Фаза 4**: Интеграция с ML пайплайнами

## 🚀 Контрибуция

Для добавления новых скриптов обработки данных:
1. Следуйте архитектурным принципам BQuant
2. Используйте существующие утилиты из `bquant.data`
3. Добавляйте comprehensive тесты
4. Документируйте API и примеры использования

## 🔗 См. также

- [BQuant Data Module](../../bquant/data/README.md)
- [Sample Data Documentation](../../bquant/data/samples/README.md)
- [Data Processing Best Practices](../../docs/data_processing.md)
