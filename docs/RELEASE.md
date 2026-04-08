# Release checklist

## 1) Проверки перед выпуском

```bash
python tasks/manage.py makemigrations --check --dry-run
python tasks/manage.py test new users
```

## 2) Сборка артефакта

```bash
git archive --format=zip --output=release-artifact.zip HEAD
```

## 3) Тег и GitHub Release

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
gh release create vX.Y.Z release-artifact.zip --title "vX.Y.Z" --notes "Release vX.Y.Z"
```

## 4) Проверка

- Убедиться, что release отображается в GitHub.
- Убедиться, что ZIP-артефакт прикреплён к релизу.
