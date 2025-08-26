# BQuant - Примеры использования

Эта папка содержит практические примеры использования библиотеки BQuant для различных задач квантового анализа финансовых рынков.

## 📋 Содержание

### 🔰 Базовые примеры

#### [`01_basic_indicators.py`](01_basic_indicators.py)
**Базовое использование технических индикаторов**

- ✅ Создание тестовых OHLCV данных
- ✅ Расчет основных индикаторов (SMA, RSI, MACD, Bollinger Bands)
- ✅ Интерпретация сигналов индикаторов
- ✅ Комбинированный технический анализ
- ✅ Сохранение результатов в CSV

**Что демонстрирует:**
```python
from bquant.indicators import calculate_moving_averages, calculate_rsi, calculate_macd
from bquant.core.config import get_indicator_params

# Простое использование индикаторов
ma_data = calculate_moving_averages(data, periods=[10, 20, 50])
rsi_data = calculate_rsi(data, period=14)
macd_data = calculate_macd(data)
```

#### [`02_macd_zone_analysis.py`](02_macd_zone_analysis.py)
**Продвинутый MACD анализ зон**

- ✅ Автоматическое определение бычьих и медвежьих зон MACD
- ✅ Расчет 20+ признаков для каждой зоны
- ✅ Статистическое тестирование торговых гипотез
- ✅ Кластеризация зон по форме (K-means)
- ✅ Анализ последовательностей зон
- ✅ Экспорт результатов в CSV

**Что демонстрирует:**
```python
from bquant.indicators.macd import MACDZoneAnalyzer, analyze_macd_zones

# Полный анализ зон MACD
analyzer = MACDZoneAnalyzer()
result = analyzer.analyze_complete(data, perform_clustering=True)

# Или быстрый анализ
result = analyze_macd_zones(data, perform_clustering=True, n_clusters=3)
```

#### [`03_data_processing.py`](03_data_processing.py)
**Работа с данными**

- ✅ Создание различных типов данных (трендовые, волатильные)
- ✅ Валидация и очистка данных
- ✅ Удаление выбросов и обработка пропусков
- ✅ Ресэмплинг данных между таймфреймами
- ✅ Расчет производных индикаторов
- ✅ Создание лаговых признаков
- ✅ Нормализация данных
- ✅ Работа со схемами данных (OHLCVRecord, DataSourceConfig)

**Что демонстрирует:**
```python
from bquant.data import create_sample_data, validate_ohlcv_data, clean_data
from bquant.data.schemas import OHLCVRecord, DataSourceConfig

# Комплексная обработка данных
data = create_sample_data("XAUUSD", "2024-01-01", "2024-01-10", "1h")
validation = validate_ohlcv_data(data)
cleaned_data = clean_data(data)
```

### 🚀 Продвинутые примеры

#### [`04_comprehensive_analysis.py`](04_comprehensive_analysis.py)
**Комплексная торговая система**

- ✅ Полный цикл создания торговой системы
- ✅ Генерация реалистичных рыночных данных с различными режимами
- ✅ Расчет множественных технических индикаторов
- ✅ Продвинутый MACD анализ зон
- ✅ Генерация комплексных торговых сигналов
- ✅ Полноценный бэктестинг с риск-менеджментом
- ✅ Подробная статистика производительности
- ✅ Генерация JSON отчетов
- ✅ Экспорт всех результатов

**Что демонстрирует:**
```python
from examples.comprehensive_analysis import ComprehensiveTradingAnalyzer

# Создание и тестирование торговой системы
analyzer = ComprehensiveTradingAnalyzer("XAUUSD", "1h")
data = analyzer.load_and_prepare_data(rows=1000)
indicators = analyzer.calculate_all_indicators()
analyzer.perform_macd_zone_analysis()
signals = analyzer.generate_trading_signals()
performance = analyzer.backtest_strategy(initial_capital=10000)
```

## 🛠️ Установка и запуск

### Предварительные требования

```bash
# Установка BQuant в режиме разработки
pip install -e .

# Дополнительные зависимости для некоторых примеров
pip install matplotlib seaborn  # Для визуализации (опционально)
```

### Запуск примеров

```bash
# Запуск любого примера из корневой папки проекта
python examples/01_basic_indicators.py
python examples/02_macd_zone_analysis.py
python examples/03_data_processing.py
python examples/04_comprehensive_analysis.py
```

## 📊 Структура результатов

После запуска примеров в папке `examples/` будут созданы файлы с результатами:

### Базовые результаты
- `indicator_results.csv` - Результаты расчета базовых индикаторов
- `sample_ohlcv_data.csv` - Тестовые OHLCV данные
- `trending_data.csv` - Данные с трендом
- `volatile_data.csv` - Высоковолатильные данные

### MACD анализ
- `comprehensive_macd_zones.csv` - Детали всех обнаруженных зон
- `comprehensive_macd_statistics.csv` - Статистики распределения зон
- `comprehensive_macd_hypothesis_tests.csv` - Результаты статистических тестов
- `comprehensive_macd_clustering.csv` - Результаты кластеризации

### Обработка данных
- `comprehensive_processed_data.csv` - Полностью обработанные данные
- `sample_ohlcv_data.csv` - Базовые OHLCV данные

### Комплексный анализ
- `comprehensive_market_data.csv` - Рыночные данные
- `comprehensive_indicators.csv` - Все рассчитанные индикаторы
- `comprehensive_signals.csv` - Торговые сигналы
- `comprehensive_trades.csv` - Журнал сделок
- `comprehensive_analysis_report_XAUUSD_YYYYMMDD_HHMMSS.json` - Полный JSON отчет

## 🎯 Ключевые возможности BQuant

### 📈 Технические индикаторы
- **5+ встроенных индикаторов**: SMA, EMA, RSI, MACD, Bollinger Bands
- **Система плагинов**: Поддержка внешних библиотек (pandas-ta, TA-Lib)
- **Фабрика индикаторов**: Унифицированное создание и управление
- **Кэширование результатов**: Оптимизация производительности

### 🎯 MACD Zone Analyzer
- **Автоматическое определение зон**: Бычьи и медвежьи зоны
- **20+ признаков зон**: Длительность, амплитуда, корреляции, экстремумы
- **Статистические тесты**: 3 торговые гипотезы с p-value
- **Кластеризация**: K-means группировка зон по форме
- **Анализ последовательностей**: Вероятности переходов между зонами

### 📊 Работа с данными
- **Множественные источники**: CSV, sample data, внешние API
- **Валидация данных**: Автоматическая проверка целостности
- **Очистка данных**: Обработка пропусков и выбросов
- **Трансформации**: Ресэмплинг, нормализация, лаговые признаки
- **Схемы данных**: Типизированные структуры (OHLCVRecord, DataSourceConfig)

### 🔧 Конфигурация и гибкость
- **Централизованная конфигурация**: Параметры индикаторов и анализа
- **Поддержка таймфреймов**: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M
- **Логгирование**: Подробное отслеживание операций
- **Обработка ошибок**: Кастомные исключения с контекстом

## 📚 Дополнительная документация

### Архитектурные принципы
- **Модульность**: Четкое разделение ответственности между модулями
- **Расширяемость**: Простое добавление новых индикаторов и анализаторов
- **Производительность**: Оптимизированные алгоритмы и кэширование
- **Надежность**: Comprehensive тестирование и обработка ошибок

### Интеграция в проекты
```python
# Быстрое начало в вашем проекте
from bquant.indicators import calculate_macd, calculate_rsi
from bquant.indicators.macd import analyze_macd_zones
from bquant.data import create_sample_data

# Создаем данные
data = create_sample_data("EURUSD", "2024-01-01", "2024-02-01", "1h")

# Рассчитываем индикаторы
macd_data = calculate_macd(data)
rsi_data = calculate_rsi(data)

# Анализируем зоны MACD
macd_analysis = analyze_macd_zones(data, perform_clustering=True)

print(f"Найдено зон: {len(macd_analysis.zones)}")
print(f"Статистических тестов: {len(macd_analysis.hypothesis_tests)}")
```

## 💡 Советы по использованию

### Производительность
- Используйте достаточное количество данных (500+ баров) для статистических тестов
- Кэшируйте результаты индикаторов при повторных вычислениях
- Настройте параметры анализа в `bquant/core/config.py`

### Отладка
- Включите детальное логгирование: `logging.basicConfig(level=logging.DEBUG)`
- Проверьте результаты валидации данных перед анализом
- Используйте сохраненные CSV файлы для анализа промежуточных результатов

### Расширение функциональности
- Создавайте собственные индикаторы наследуясь от `BaseIndicator`
- Добавляйте новые признаки зон в `MACDZoneAnalyzer.calculate_zone_features()`
- Модифицируйте торговые сигналы в `ComprehensiveTradingAnalyzer`

## 🤝 Вклад в проект

При создании новых примеров:
1. Следуйте структуре существующих примеров
2. Добавьте подробные комментарии и docstring'и
3. Включите обработку ошибок и валидацию
4. Обновите этот README.md
5. Создайте тесты для новых функций

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи BQuant: `logs/bquant.log`
2. Убедитесь в корректности данных через `validate_ohlcv_data()`
3. Проверьте версии зависимостей: `pip list`
4. Изучите исходный код в `bquant/` для понимания работы

---

**BQuant** - Современная библиотека для квантового анализа финансовых рынков с профессиональной архитектурой и comprehensive функциональностью! 🚀
