# Task 01: Рефакторинг структуры MCP серверов

## Описание
Переработка базовой структуры MCP серверов Memory Bank и HIL для соответствия новой архитектуре с использованием Resources и Prompts вместо только Tools.

## Что нужно сделать

### 1. Анализ и подготовка
- Изучить текущую реализацию `server.py` и `mcp_server.py` в memory_bank
- Определить какие текущие tools должны стать resources (статичные данные)
- Определить какие команды должны стать prompts (implement-component, ask)

### 2. Создание новой структуры MCP
- Разделить `server.py` на:
  - `mcp_tools.py` - активные операции (journal-note, next-increment)
  - `mcp_resources.py` - чтение данных (architecture, progress, state)
  - `mcp_prompts.py` - команды через промпты (implement-component)
  - `utils.py` - вспомогательные функции (пагинация, поиск путей)

### 3. Обновление HIL MCP
- Переименовать `ask-human` tool в более понятное название
- Добавить `ask` prompt для замены слеш-команды `/voice`

## Что сохранить из текущей реализации
- Логику работы с путями к Memory Bank и рабочей директории
- Функции пагинации `_paginate_content`
- Базовую логику поиска и загрузки файлов

## Что удалить
- Старые tools: get-focus, get-progress, current-task, current-epic, current-component
- update-task-status, next-task, next-epic (заменены на next-increment)
- Дублирующие функции в mcp_server.py

## Результат
- Чистая структура с разделением на tools/resources/prompts
- Подготовленная база для новой логики инкрементов

## Время: 4-5 часов