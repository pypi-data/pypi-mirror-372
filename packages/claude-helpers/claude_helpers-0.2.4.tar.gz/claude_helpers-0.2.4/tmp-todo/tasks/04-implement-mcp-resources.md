# Task 04: Реализация MCP Resources

## Описание
Создание MCP Resources для предоставления статичных данных из Memory Bank через правильную архитектуру MCP.

## Что нужно сделать

### 1. Создать mcp_resources.py с ресурсами:
```python
@mcp.resource("/architecture/tech-context/*")
def get_tech_context_files():
    # Возврат всех файлов из tech-context папки
    
@mcp.resource("/architecture/{release}/{component}/component.md")
def get_component_spec(release: str, component: str):
    # Прокси к спецификации компонента
    
@mcp.resource("/todo/{release}/{component}/increment.md")
def get_current_increment(release: str, component: str):
    # Текущий инкремент из состояния
    
@mcp.resource("/todo/{release}/{component}/decomposition.md")
def get_decomposition(release: str, component: str):
    # Декомпозиция компонента
    
@mcp.resource("/progress/{release}/{component}/journal.md")
def get_journal(release: str, component: str):
    # Журнал текущего инкремента
    
@mcp.resource("/progress/{release}/{component}/state.md")
def get_combined_state(release: str, component: str):
    # Комбинация initial-state + progress-state
```

### 2. Реализация пагинации для больших ресурсов
- Добавить параметр `page` в URI шаблоны где нужно
- Возвращать metadata о доступных страницах
- Использовать существующую `_paginate_content`

### 3. Обработка путей и fallback
- Проверка существования файлов
- Корректные сообщения об ошибках
- Динамическая загрузка файлов из tech-context/*

### 4. Форматирование ответов
- Правильная сериализация для MCP
- Поддержка markdown контента
- Metadata для навигации

## Что использовать из текущей реализации
- Логику поиска путей к Memory Bank
- Функции чтения файлов с обработкой ошибок
- Пагинацию

## Новое
- Использование декоратора @mcp.resource вместо tool
- URI-based routing для ресурсов
- Автоматическое обнаружение файлов в tech-context

## Результат
- Чистое разделение статичных данных от активных операций
- Правильная MCP архитектура с Resources
- Поддержка больших файлов через пагинацию

## Время: 5-6 часов