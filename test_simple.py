import json
import sys
import os
from unittest.mock import Mock, patch

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'amplify/backend/function/siteUserHandler/src'))

# Variables d'environnement pour les tests
os.environ['STORAGE_SITEUSERTABLE_NAME'] = 'siteUserTable'

# Import de nos modules
from index import handler
from user_service import add_user, get_user

def test_add_user_success():
    """Test d'ajout d'un utilisateur avec succès"""
    with patch('user_service.get_dynamodb_table') as mock_get_table:
        # Configuration du mock
        mock_table = Mock()
        mock_table.get_item.return_value = {}  # Pas d'utilisateur existant
        mock_table.put_item.return_value = {}  # Succès de l'insertion
        mock_get_table.return_value = mock_table
        
        # Données d'entrée
        user_data = {
            'userId': 'user123',
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        
        # Appel de la fonction
        result = add_user(user_data)
        
        # Vérifications
        assert result['success'] is True
        assert result['message'] == 'User created successfully'
        assert result['userId'] == 'user123'
        print("✅ Test add_user_success passé")

def test_add_user_missing_fields():
    """Test d'ajout d'un utilisateur avec des champs manquants"""
    user_data = {
        'userId': 'user123'
        # Manque name et email
    }
    
    result = add_user(user_data)
    
    assert result['success'] is False
    assert 'Missing required fields' in result['error']
    print("✅ Test add_user_missing_fields passé")

def test_get_user_success():
    """Test de récupération d'un utilisateur avec succès"""
    with patch('user_service.get_dynamodb_table') as mock_get_table:
        # Configuration du mock
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': 'user123',
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        }
        mock_get_table.return_value = mock_table
        
        result = get_user('user123')
        
        assert result['success'] is True
        assert result['user']['userId'] == 'user123'
        assert result['user']['name'] == 'John Doe'
        print("✅ Test get_user_success passé")

def test_handler_post_user():
    """Test du handler pour POST /user"""
    with patch('index.add_user') as mock_add_user:
        # Configuration du mock
        mock_add_user.return_value = {
            'success': True,
            'message': 'User created successfully',
            'userId': 'user123'
        }
        
        event = {
            'httpMethod': 'POST',
            'path': '/user',
            'body': json.dumps({
                'userId': 'user123',
                'name': 'John Doe',
                'email': 'john@example.com'
            })
        }
        context = {}
        
        response = handler(event, context)
        
        assert response['statusCode'] == 201
        body = json.loads(response['body'])
        assert body['message'] == 'User created successfully'
        print("✅ Test handler_post_user passé")

def test_handler_get_user():
    """Test du handler pour GET /user"""
    with patch('index.get_user') as mock_get_user:
        # Configuration du mock
        mock_get_user.return_value = {
            'success': True,
            'user': {
                'userId': 'user123',
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        }
        
        event = {
            'httpMethod': 'GET',
            'path': '/user',
            'queryStringParameters': {
                'userId': 'user123'
            }
        }
        context = {}
        
        response = handler(event, context)
        
        assert response['statusCode'] == 200
        body = json.loads(response['body'])
        assert body['userId'] == 'user123'
        print("✅ Test handler_get_user passé")

if __name__ == '__main__':
    print("🧪 Lancement des tests unitaires TDD")
    print("=" * 40)
    
    try:
        test_add_user_success()
        test_add_user_missing_fields()
        test_get_user_success()
        test_handler_post_user()
        test_handler_get_user()
        
        print("\n🎉 Tous les tests sont passés avec succès !")
        print("Votre implémentation TDD fonctionne parfaitement en local !")
        
    except Exception as e:
        print(f"\n❌ Erreur dans les tests: {e}")
        raise 