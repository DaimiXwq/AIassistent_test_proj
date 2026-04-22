# Офлайн wheelhouse: включаем транзитивные зависимости

Короткий ответ: **да, у каждого пакета из `requirements.txt` есть транзитивные зависимости**.

Если wheelhouse собирается правильно, **не нужно вручную перечислять** все транзитивные зависимости в `requirements.txt`.

## Рекомендуемый процесс (машина с интернетом)

1. Создайте чистое виртуальное окружение.
2. Обновите инструменты упаковки.
3. Скачайте колёса (`wheels`) для `requirements.txt` **вместе с зависимостями**.
4. Зафиксируйте точный набор установленных пакетов (`pip freeze`) для воспроизводимости.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel

# Скачивает прямые + транзитивные зависимости в wheelhouse/
pip download -r requirements.txt -d wheelhouse

# Опционально, но рекомендуется: проверить установку только из локального wheelhouse
pip install --no-index --find-links=wheelhouse -r requirements.txt

# Фиксируем точный установленный набор (включая транзитивные зависимости)
pip freeze > requirements.lock.txt
```

## Установка на офлайн-машине

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install --no-index --find-links=wheelhouse -r requirements.txt
```

## Важные замечания

- Если офлайн-целевая ОС/Python отличаются от онлайн-машины сборки, готовьте wheelhouse строго под целевую платформу.
- Колёса `torch` и `tokenizers` платформозависимы; скачивайте/собирайте их под ту же версию Python и архитектуру, что и у офлайн-хоста.
- Для `sentence-transformers` заранее скачайте файлы модели (например, `all-MiniLM-L6-v2`) в локальный путь.
