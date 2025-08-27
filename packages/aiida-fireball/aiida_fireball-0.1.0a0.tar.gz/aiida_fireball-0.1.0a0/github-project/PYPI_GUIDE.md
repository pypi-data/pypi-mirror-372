# Guide de Publication PyPI pour aiida-fireball

## Étapes pour publier sur PyPI et faire apparaître les badges

### 1. Créer un compte PyPI
- Allez sur https://pypi.org et créez un compte
- Pour tester d'abord : https://test.pypi.org

### 2. Générer un token API
1. Dans PyPI : Account settings → API tokens
2. Créez un token "For entire account" ou spécifique au projet

### 3. Configurer GitHub Secrets
1. GitHub repo → Settings → Secrets and variables → Actions
2. Créez `PYPI_API_TOKEN` avec votre token PyPI

### 4. Publication manuelle (première fois)
```bash
# Nettoyer le build précédent
rm -rf dist/ build/

# Construire le package
python -m build

# Publier sur TestPyPI (optionnel, pour tester)
python -m twine upload --repository testpypi dist/*

# Publier sur PyPI (réel)
python -m twine upload dist/*
```

### 5. Publication automatique via GitHub
Une fois le token configuré dans GitHub :
```bash
# Créer une release avec tag
git tag v0.1.1
git push --tags

# Ou créer une release via l'interface GitHub
```

### 6. Vérifier les badges
Après publication, les badges apparaîtront automatiquement :
- [![PyPI version](https://img.shields.io/pypi/v/aiida-fireball.svg)](https://pypi.org/project/aiida-fireball/)
- [![Python versions](https://img.shields.io/pypi/pyversions/aiida-fireball.svg)](https://pypi.org/project/aiida-fireball/)

## Notes importantes
- Le nom `aiida-fireball` doit être unique sur PyPI
- Première publication nécessite le token avec permission "entire account"
- Les publications suivantes peuvent utiliser un token projet-spécifique
