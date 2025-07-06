# Guide TDD - Projet AWS Lambda avec DynamoDB

## 📋 Objectif
Ce projet implémente une approche **Test-Driven Development (TDD)** pour créer des fonctions AWS Lambda qui gèrent des utilisateurs dans une base de données DynamoDB, le tout exécutable en local.

## 🏗️ Architecture du Projet

```
TDD-Amplify-IIM-re/
├── amplify/backend/function/siteUserHandler/src/
│   ├── index.py              # Handler principal Lambda
│   ├── user_service.py       # Logic métier pour les utilisateurs
│   └── __init__.py          # Package Python
├── test_simple.py           # Tests unitaires simplifiés
└── README_TDD.md           # Ce guide
```

## 🔧 Fonctionnalités Implémentées

### 📝 API REST
- **POST /user** : Créer un nouvel utilisateur
- **GET /user?userId=XXX** : Récupérer un utilisateur par son ID

### 👤 Modèle Utilisateur
```json
{
  "userId": "string",
  "name": "string", 
  "email": "string"
}
```

## 🧪 Méthodologie TDD Appliquée

### 1. **Red** - Écrire les tests qui échouent
Les tests dans `test_simple.py` définissent le comportement attendu :
- ✅ Création d'utilisateur avec succès
- ✅ Validation des champs requis
- ✅ Récupération d'utilisateur existant
- ✅ Gestion des erreurs HTTP

### 2. **Green** - Écrire le code minimal qui passe
- `user_service.py` : Fonctions `add_user()` et `get_user()`
- `index.py` : Handler HTTP qui route les requêtes

### 3. **Refactor** - Améliorer le code
- Séparation des responsabilités (service vs handler)
- Gestion d'erreurs cohérente
- Documentation et types de retour clairs

## 🚀 Lancement des Tests

### Méthode Simple (Recommandée)
```bash
python test_simple.py
```

### Avec pytest (si installé)
```bash
pip install pytest
python -m pytest test_simple.py -v
```

## 📊 Résultat Attendu
```
🧪 Lancement des tests unitaires TDD
========================================
✅ Test add_user_success passé
✅ Test add_user_missing_fields passé
✅ Test get_user_success passé
✅ Test handler_post_user passé
✅ Test handler_get_user passé

🎉 Tous les tests sont passés avec succès !
```

## 🛠️ Technologies Utilisées

- **Python 3.9** - Langage principal
- **boto3** - SDK AWS pour DynamoDB
- **unittest.mock** - Simulation des services AWS en local
- **AWS Lambda** - Fonction serverless
- **DynamoDB** - Base de données NoSQL (simulée)

## 💡 Avantages de cette Approche TDD

1. **Développement Local** : Pas besoin de déployer sur AWS pour tester
2. **Tests Rapides** : Exécution en quelques secondes
3. **Confiance** : Code testé avant déploiement
4. **Documentation Vivante** : Les tests documentent le comportement attendu
5. **Refactoring Sûr** : Les tests protègent contre les régressions

## 🎯 Concepts TDD Démontrés

- **Cycle Red-Green-Refactor**
- **Tests unitaires** avec mocks
- **Tests d'intégration** du handler
- **Validation des entrées**
- **Gestion des codes d'erreur HTTP**
- **Séparation des couches** (présentation vs métier)

## 🔄 Pour Étendre le Projet

1. Ajouter de nouveaux tests (DELETE, UPDATE)
2. Implémenter les fonctions correspondantes
3. Suivre le cycle TDD : Red → Green → Refactor

## 📚 Ressources pour Aller Plus Loin

- [Guide TDD de Kent Beck](https://www.amazon.fr/Test-Driven-Development-Kent-Beck/dp/0321146530)
- [Documentation AWS Lambda](https://docs.aws.amazon.com/lambda/)
- [Mocking en Python](https://docs.python.org/3/library/unittest.mock.html)

---

**Bon cours de TDD ! 🎓** 