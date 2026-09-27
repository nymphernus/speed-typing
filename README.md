# Speed Typing Test

Приложение для проверки скорости печати с графическим интерфейсом на Tkinter.

## Возможности

- **Импорт документов**: Поддержка форматов `.docx`, `.doc`, `.txt`
- **Двухязычность**: Извлечение текста на английском и русском языках
- **Два режима работы**:
  - Обычный режим — подсчёт времени на весь текст и на каждое слово
  - Режим с таймером — количество слов за ограниченное время
- **Статистика в реальном времени**: WPM, точность, время на слово
- **Визуальная подсветка**: Текущее слово подчёркивается, завершённые — выделяются зелёным
- **Масштабируемый интерфейс**: Окно можно растягивать, все элементы адаптируются

## Установка

### 1. Создание виртуального окружения

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

## Запуск

### Вариант 1: Через скрипт (Windows)

```bat
run.bat
```

### Вариант 2: Напрямую

```bash
# Windows
venv\Scripts\python.exe -m src.main

# Linux/macOS
python3 -m src.main
```

## Тестирование

```bash
# Запуск всех тестов
python -m unittest discover tests

# Запуск конкретного модуля тестов
python -m unittest tests.test_document_parser
python -m unittest tests.test_typing_engine
python -m unittest tests.test_timer
```

## Структура проекта

```
speed-typing/
├── venv/                   # Виртуальное окружение
├── src/
│   ├── __init__.py
│   ├── main.py            # Точка входа
│   ├── app.py             # GUI приложение (Tkinter)
│   ├── document_parser.py # Парсинг документов
│   ├── typing_engine.py   # Логика набора текста
│   └── timer.py           # Таймеры
├── tests/
│   ├── __init__.py
│   ├── test_document_parser.py
│   ├── test_typing_engine.py
│   └── test_timer.py
├── run.bat                # Скрипт запуска (Windows)
├── requirements.txt
├── .gitignore
└── README.md
```

## Использование

1. **Открытие документа**: Файл → Открыть (или Ctrl+O)
2. **Выбор режима**: Обычный или С таймером
3. **Начало работы**: Нажмите "Старт"
4. **Набор текста**: Вводите текст — слова проверяются автоматически при вводе последней буквы
5. **Результаты**: По завершении появится окно со статистикой

## Зависимости

- `python-docx` — для чтения .docx файлов
- `olefile` — для чтения .doc файлов
