# Examples - Примеры использования BQuant

## 📚 Обзор

Примеры использования BQuant демонстрируют различные сценарии применения библиотеки от простых до сложных.

## 🗂️ Категории примеров

### 🚀 [Basic Examples](basic/) - Базовые примеры
- **hello_world.py** - Первый пример с BQuant
- **load_data.py** - Загрузка и обработка данных
- **simple_macd.py** - Простой анализ MACD
- **basic_visualization.py** - Базовая визуализация

### 📈 [Advanced Examples](advanced/) - Продвинутые примеры
- **macd_zone_analysis.py** - Полный анализ MACD с зонами
- **statistical_analysis.py** - Статистический анализ данных
- **custom_indicators.py** - Создание собственных индикаторов
- **performance_optimization.py** - Оптимизация производительности

### 🌍 [Real-world Cases](real_world/) - Реальные кейсы
- **trading_analysis.py** - Анализ торговых стратегий
- **market_research.py** - Исследование рынка
- **risk_management.py** - Управление рисками
- **portfolio_analysis.py** - Анализ портфеля

### 🔗 [Integration Examples](integration/) - Интеграция
- **pandas_integration.py** - Интеграция с pandas
- **matplotlib_integration.py** - Интеграция с matplotlib
- **jupyter_integration.py** - Работа в Jupyter
- **external_data.py** - Работа с внешними данными

## 🎯 Быстрый старт с примерами

### 1. Простой анализ MACD

```python
# examples/basic/simple_macd.py
import bquant as bq
from bquant.data.samples import get_sample_data
from bquant.indicators import MACDZoneAnalyzer

# Загружаем данные
data = get_sample_data('tv_xauusd_1h')

# Создаем анализатор
analyzer = MACDZoneAnalyzer()

# Выполняем анализ
result = analyzer.analyze_complete(data)

# Выводим результаты
print(f"Найдено зон: {len(result.zones)}")
print(f"Статистика: {result.statistics}")
```

### 2. Визуализация с зонами

```python
# examples/basic/basic_visualization.py
from bquant.visualization import FinancialCharts
from bquant.data.samples import get_sample_data
from bquant.indicators import MACDZoneAnalyzer

# Данные и анализ
data = get_sample_data('tv_xauusd_1h')
analyzer = MACDZoneAnalyzer()
result = analyzer.analyze_complete(data)

# Создаем график
charts = FinancialCharts()
fig = charts.plot_macd_with_zones(data, result.zones)
fig.show()
```

### 3. Статистический анализ

```python
# examples/advanced/statistical_analysis.py
from bquant.analysis.statistical import run_all_hypothesis_tests
from bquant.data.samples import get_sample_data
from bquant.indicators import MACDZoneAnalyzer

# Получаем данные для анализа
data = get_sample_data('tv_xauusd_1h')
analyzer = MACDZoneAnalyzer()
result = analyzer.analyze_complete(data)

# Статистические тесты
zones_info = {
    'zones_features': [zone.features for zone in result.zones if zone.features],
    'zones': result.zones,
    'statistics': result.statistics
}

hypothesis_results = run_all_hypothesis_tests(zones_info)
print("Статистические тесты:", hypothesis_results)
```

## 📊 Структура каждого примера

### 📖 Заголовок и описание
```python
"""
Пример: Анализ MACD с зонами

Этот пример демонстрирует:
- Загрузку sample данных
- Создание анализатора MACD
- Выполнение полного анализа
- Визуализацию результатов

Автор: BQuant Team
Дата: 2024
"""
```

### 🔧 Импорты и настройка
```python
import bquant as bq
from bquant.data.samples import get_sample_data
from bquant.indicators import MACDZoneAnalyzer
from bquant.visualization import FinancialCharts

# Настройка логирования
import logging
logging.basicConfig(level=logging.INFO)
```

### 💻 Основной код
```python
def main():
    """Основная функция примера"""
    
    # 1. Загрузка данных
    print("Загружаем данные...")
    data = get_sample_data('tv_xauusd_1h')
    
    # 2. Анализ
    print("Выполняем анализ...")
    analyzer = MACDZoneAnalyzer()
    result = analyzer.analyze_complete(data)
    
    # 3. Результаты
    print("Результаты анализа:")
    print(f"  - Зон найдено: {len(result.zones)}")
    print(f"  - Статистика: {result.statistics}")
    
    # 4. Визуализация
    print("Создаем визуализацию...")
    charts = FinancialCharts()
    fig = charts.plot_macd_with_zones(data, result.zones)
    fig.show()

if __name__ == "__main__":
    main()
```

### 📋 Документация
- **Описание** - Что делает пример
- **Требования** - Необходимые зависимости
- **Запуск** - Как запустить пример
- **Результаты** - Что ожидать на выходе

## 🚀 Как запускать примеры

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/bquant.git
cd bquant
```

### 2. Установка зависимостей
```bash
pip install -e .
```

### 3. Запуск примера
```bash
# Базовый пример
python docs/examples/basic/simple_macd.py

# Продвинутый пример
python docs/examples/advanced/macd_zone_analysis.py

# С параметрами
python docs/examples/real_world/trading_analysis.py --symbol XAUUSD --timeframe 1h
```

### 4. В Jupyter Notebook
```python
# Загружаем пример как модуль
import sys
sys.path.append('docs/examples/basic')
import simple_macd

# Запускаем
simple_macd.main()
```

## 💡 Советы по использованию примеров

### 🎯 Для изучения
- **Начните с basic/** - Освойте базовые концепции
- **Изучайте код** - Читайте комментарии и docstrings
- **Экспериментируйте** - Изменяйте параметры и наблюдайте результаты
- **Задавайте вопросы** - Если что-то непонятно

### 🔧 Для разработки
- **Используйте как шаблоны** - Адаптируйте под свои нужды
- **Изучайте паттерны** - Обратите внимание на структуру кода
- **Тестируйте изменения** - Проверяйте работу после модификаций
- **Документируйте** - Добавляйте комментарии к своим изменениям

### 🚀 Для продакшена
- **Адаптируйте под данные** - Замените sample данные на реальные
- **Добавьте обработку ошибок** - Используйте try/except блоки
- **Оптимизируйте производительность** - Примените техники из performance/
- **Настройте логирование** - Добавьте информативные логи

## 🔗 Связанные разделы

- **[User Guide](../user_guide/)** - Руководство пользователя
- **[API Reference](../api/)** - Справочник API
- **[Tutorials](../tutorials/)** - Обучающие материалы
- **[Developer Guide](../developer_guide/)** - Для разработчиков

## 🤝 Вклад в примеры

### Добавление нового примера
1. **Создайте файл** в соответствующей папке
2. **Добавьте документацию** - описание, требования, запуск
3. **Протестируйте** - убедитесь что пример работает
4. **Создайте PR** - предложите изменения

### Структура нового примера
```python
"""
Название: Краткое описание

Подробное описание что делает пример и как его использовать.

Требования:
- bquant
- pandas
- matplotlib

Запуск:
python examples/category/example_name.py

Автор: Ваше имя
Дата: YYYY-MM-DD
"""

import bquant as bq
# ... остальные импорты

def main():
    """Основная функция"""
    pass

if __name__ == "__main__":
    main()
```

---

**Начать изучение:** [Basic Examples](basic/) 🚀
