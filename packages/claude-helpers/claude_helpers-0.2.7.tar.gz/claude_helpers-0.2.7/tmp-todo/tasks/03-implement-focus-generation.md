# Task 03: Реализация генерации фокусов для ролей

## Описание
Создание системы генерации динамических фокусов для каждой роли (PM, dev, tech-lead) с использованием Claude Code SDK и шаблонов.

## Что нужно сделать

### 1. MCP Tools для фокусов
- `get-pm-focus(release, component, page=1)` - фокус для PM на уровне компонента
- `get-dev-focus(release, component, page=1)` - фокус для dev на уровне инкремента
- `get-tech-lead-focus(release, component, page=1)` - фокус для tech-lead

### 2. Логика генерации фокусов
Для каждой роли:
- Проверка существования файла фокуса в текущем инкременте
- Если нет - генерация через формулу:
  - PM: distilled_product + component + decomposition + state
  - Dev: distilled_product + component + increment + state
  - Tech-lead: distilled_product + component + increment + state

### 3. Интеграция Claude Code SDK
```python
from claude_code_sdk import query, ClaudeCodeOptions

async def generate_product_distillation(memory_bank_path, working_dir):
    # Загрузка промпта из templates/workflow/memory-bank/product-distillation.md
    # Запуск Claude Code SDK с контекстом
    # Возврат дистиллированного продукта
```

### 4. Работа с шаблонами
- Приоритет: Memory Bank templates > встроенные в claude-helpers
- Шаблоны фокусов: `templates/progress/{role}-focus.md`
- Промпт дистилляции: `templates/workflow/memory-bank/product-distillation.md`

### 5. Поддержка пагинации
- Использовать существующую `_paginate_content`
- Возвращать metadata о страницах в ответе

## Что использовать из текущей реализации
- Функции пагинации
- Логику загрузки шаблонов с fallback
- Базовую структуру генерации фокусов

## Что изменить
- Убрать старую логику epic/task
- Адаптировать под инкременты
- Добавить вызовы Claude Code SDK

## Результат
- Автоматическая генерация фокусов для всех ролей
- Кеширование в файлах для повторного использования
- Поддержка больших документов через пагинацию

## Время: 8-10 часов