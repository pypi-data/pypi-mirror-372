# Task 02: Реализация логики инкрементов

## Описание
Внедрение новой концепции инкрементов взамен эпиков/задач. Инкременты - атомарные единицы работы для цикла owner<->PM<->dev<->tech-lead.

## Что нужно сделать

### 1. Обновление моделей данных
- Создать модель `IncrementState` взамен `FeatureState`
- Добавить поля: current_increment, increment_status, implementation_overview
- Удалить поля: current_epic, current_task

### 2. Реализация новых MCP Tools
- `journal-note(release, component, role, message)` - запись в журнал инкремента
- `next-increment(release, component)` - переход к следующему инкременту с генерацией overview

### 3. Логика работы с состоянием
- Чтение текущего инкремента из `progress-state.md`
- Обновление состояния при переходе между инкрементами
- Генерация implementation overview через Claude Code SDK

### 4. Структура папок
```
progress/releases/{release}/{component}/
├── increments/
│   ├── {increment-id}/
│   │   ├── journal.md
│   │   ├── pm-focus.md (генерируется при необходимости)
│   │   ├── dev-focus.md (генерируется при необходимости)
│   │   └── tech-lead-focus.md (генерируется при необходимости)
├── progress-state.md
└── initial-state.md (копируется из implementation)
```

## Что использовать из текущей реализации
- Базовые функции работы с YAML headers
- Логику создания папок и файлов
- Шаблоны journal записей

## Что изменить
- Переработать `_ensure_component_state` для работы с инкрементами
- Адаптировать пути к новой структуре increments/

## Результат
- Полноценная поддержка инкрементов
- Автоматическое управление состоянием компонента
- Генерация overview при завершении инкремента

## Время: 6-7 часов