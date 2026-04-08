# Cоздание веб-приложения для управления проектами и задачами с использованием Python и Django

## Главная страница 
**Регистрация - для администраторов,**
**Вход - для подчиненных**
<p><img width="1566" height="873" alt="image" src="https://github.com/user-attachments/assets/b966f83d-1beb-44b8-bde8-cf22943bde3c" /></p>


## Функции ***администратора***

Администратор заведует полностью всем, что происходит на сайте.

В первую очередь он регистрируется сам:

<img width="1280" height="678" alt="image" src="https://github.com/user-attachments/assets/57f24bed-0141-4da1-b9ac-e47d76555d58" />

<img width="681" height="325" alt="image" src="https://github.com/user-attachments/assets/61382812-2678-44ab-b7a0-d0a8808f313a" />


Дальше регистрирует новых работников, дает им логин и пароль для доступа к их аккаунту.

<p><img width="1641" height="1014" alt="image" src="https://github.com/user-attachments/assets/60491c53-fbdf-4064-96e2-4ce5fac1118b" /></p>


Также он может создать проект:

<p><img width="895" height="899" alt="image" src="https://github.com/user-attachments/assets/93c428ed-c6d2-46e3-8a04-8fd1fe24709b" /></p>

и задачу:

<p><img width="1073" height="830" alt="image" src="https://github.com/user-attachments/assets/918df2a2-d71e-4fe8-8c53-3e60843234a4" /></p>

отредактировать нужный ему проект:

<p><img width="785" height="853" alt="image" src="https://github.com/user-attachments/assets/c65f40ca-65eb-4e77-b5c9-ff3deb8704d5" /></p>

добавить комментарии к задаче:

<p><img width="1599" height="746" alt="image" src="https://github.com/user-attachments/assets/6dea2229-27ae-47a0-9a43-0d764743c3be" /></p>

просмотреть историю изменения в задаче:

<p><img width="987" height="574" alt="image" src="https://github.com/user-attachments/assets/8067b017-40cb-44cf-8b0e-35b61753d02d" /></p>

контролировать нагрузку на себя и своих сотрудников:

<img width="1635" height="675" alt="image" src="https://github.com/user-attachments/assets/3903ad9f-3f0a-428c-a189-50edb0f53198" />



## Функции для ***пользователя***

Функции пользователя похожи на администратора, но с некоторыми ограничениями  по доступности.
По данным, которые дает админ, пользователь входит в свой аккаунт.

<p><img width="1804" height="994" alt="image" src="https://github.com/user-attachments/assets/ab3349eb-b951-4e36-9bf6-0b139ea2c000" /></p>
 

Можно отслеживать свои проекты и фильтровать их по нужным данным

<img width="1662" height="755" alt="image" src="https://github.com/user-attachments/assets/0b12ed5a-33b8-43b9-845e-3590aa6d276f" />


а также добавлять новые проекты

![image](https://github.com/user-attachments/assets/b504feaa-7234-4096-aee4-fa26bf35fba5)

отслеживать свою нагрузку и эффективность

<img width="1687" height="802" alt="image" src="https://github.com/user-attachments/assets/c5bef1a1-b888-4953-8231-98bb6989cc27" />




## Быстрый запуск (локально)

1. Установите Python 3.12+.
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Выполните миграции:

```bash
python tasks/manage.py migrate
```

4. Запустите сервер:

```bash
python tasks/manage.py runserver
```

Приложение будет доступно по адресу `http://127.0.0.1:8000/`.

## Тестирование и сборка

- Локальный запуск тестов:
  - `python tasks/manage.py test new users`
- Проверка, что миграции актуальны:
  - `python tasks/manage.py makemigrations --check --dry-run`
- CI запускается через GitHub Actions из файла `.github/workflows/ci.yml` и выполняет:
  - установку зависимостей;
  - проверку миграций;
  - автоматические тесты;
  - сборку ZIP-артефакта релиза.

## Документация кода (Doxygen)

Для генерации документации используется файл `Doxyfile` и Doxygen-совместимые комментарии в Python-коде.

```bash
doxygen Doxyfile
```

HTML-документация будет создана в каталоге `docs/doxygen/html`.

## Инструкция по выпуску релиза

1. Убедитесь, что тесты проходят:
   - `python tasks/manage.py test new users`
2. Создайте ZIP-артефакт (локально):
   - `git archive --format=zip --output=release-artifact.zip HEAD`
3. Создайте тег:
   - `git tag vX.Y.Z`
4. Опубликуйте релиз с артефактом:
   - `gh release create vX.Y.Z release-artifact.zip --title "vX.Y.Z" --notes "Release vX.Y.Z"`
