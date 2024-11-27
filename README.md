# Ассемблер и Интерпретатор для Учебной Виртуальной Машины (УВМ)

## Описание проекта

Проект реализует ассемблер и интерпретатор для учебной виртуальной машины (УВМ).

### Основные компоненты:
1. **Ассемблер**: Преобразует текстовое представление программ УВМ в бинарный формат, пригодный для выполнения интерпретатором.
2. **Интерпретатор**: Выполняет бинарные инструкции, сохраняя результаты выполнения в указанном диапазоне памяти.
3. **Формат логов и результатов**: Используется формат YAML для удобства чтения и анализа.

---

## Возможности

- Ассемблирование текстового представления команд в бинарный файл.
- Логирование процесса ассемблирования в формате YAML (ключи и значения).
- Интерпретация бинарных файлов с выполнением команд УВМ.
- Сохранение результатов работы интерпретатора в файл (формат YAML).
- Тесты для проверки работы всех команд УВМ.

---

## Список команд УВМ

*Добавьте описание всех команд здесь, например:*
- **CONST_LOAD**: Загрузка константы в регистр.
- **MEMORY_WRITE**: Сохранение константы из регистра в память.
- **MEMORY_READ**: Считывание константы из памяти.
- **MUL**: Умножение константы из регистра и константы из памяти.