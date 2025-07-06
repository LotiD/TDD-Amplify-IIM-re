import json
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend/function/siteUserHandler/src'))

# Import de nos modules après avoir configuré le path
try:
    from index import handler
    from user_service import add_user, get_user
except ImportError:
    # Si l'import direct ne fonctionne pas, essayer avec le chemin complet
    import importlib.util
    
    # Import de index
    spec = importlib.util.spec_from_file_location(
        "index", 
        os.path.join(os.path.dirname(__file__), '../backend/function/siteUserHandler/src/index.py')
    )
    index_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(index_module)
    handler = index_module.handler
    
    # Import de user_service
    spec = importlib.util.spec_from_file_location(
        "user_service", 
        os.path.join(os.path.dirname(__file__), '../backend/function/siteUserHandler/src/user_service.py')
    )
    user_service_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(user_service_module)
    add_user = user_service_module.add_user
    get_user = user_service_module.get_user

class TestUserService:
    """Tests pour les fonctions de service utilisateur avec mocks simples"""
    
    @patch('user_service.get_dynamodb_table')
    def test_add_user_success(self, mock_get_table):
        """Test d'ajout d'un utilisateur avec succès"""
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
        
        # Vérifier que les bonnes méthodes ont été appelées
        mock_table.get_item.assert_called_once_with(Key={'userId': 'user123'})
        mock_table.put_item.assert_called_once_with(Item=user_data)
    
    def test_add_user_missing_fields(self):
        """Test d'ajout d'un utilisateur avec des champs manquants"""
        user_data = {
            'userId': 'user123'
            # Manque name et email
        }
        
        result = add_user(user_data)
        
        assert result['success'] is False
        assert 'Missing required fields' in result['error']
        assert 'name' in result['error']
        assert 'email' in result['error']
    
    @patch('user_service.get_dynamodb_table')
    def test_add_user_already_exists(self, mock_get_table):
        """Test d'ajout d'un utilisateur qui existe déjà"""
        # Configuration du mock - utilisateur existant
        mock_table = Mock()
        mock_table.get_item.return_value = {
            'Item': {
                'userId': 'user123',
                'name': 'Existing User',
                'email': 'existing@example.com'
            }
        }
        mock_get_table.return_value = mock_table
        
        user_data = {
            'userId': 'user123',
            'name': 'John Doe',
            'email': 'john@example.com'
        }
        
        result = add_user(user_data)
        
        assert result['success'] is False
        assert 'already exists' in result['error']
        
        # Vérifier que put_item n'a pas été appelé
        mock_table.put_item.assert_not_called()
    
    @patch('user_service.get_dynamodb_table')
    def test_get_user_success(self, mock_get_table):
        """Test de récupération d'un utilisateur avec succès"""
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
        assert result['user']['email'] == 'john@example.com'
        
        mock_table.get_item.assert_called_once_with(Key={'userId': 'user123'})
    
    @patch('user_service.get_dynamodb_table')
    def test_get_user_not_found(self, mock_get_table):
        """Test de récupération d'un utilisateur qui n'existe pas"""
        # Configuration du mock - pas d'utilisateur trouvé
        mock_table = Mock()
        mock_table.get_item.return_value = {}  # Pas d'Item dans la réponse
        mock_get_table.return_value = mock_table
        
        result = get_user('nonexistent')
        
        assert result['success'] is False
        assert 'not found' in result['error']
    
    def test_get_user_missing_userid(self):
        """Test de récupération sans userId"""
        result = get_user('')
        
        assert result['success'] is False
        assert 'required' in result['error'].lower()

class TestHandlerIntegration:
    """Tests d'intégration pour la fonction handler"""
    
    @patch('index.add_user')
    def test_handler_post_user_success(self, mock_add_user):
        """Test du handler pour POST /user avec succès"""
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
        assert body['userId'] == 'user123'
    
    @patch('index.add_user')
    def test_handler_post_user_error(self, mock_add_user):
        """Test du handler pour POST /user avec erreur"""
        # Configuration du mock
        mock_add_user.return_value = {
            'success': False,
            'error': 'Missing required fields: name, email'
        }
        
        event = {
            'httpMethod': 'POST',
            'path': '/user',
            'body': json.dumps({'userId': 'user123'})
        }
        context = {}
        
        response = handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
    
    @patch('index.get_user')
    def test_handler_get_user_success(self, mock_get_user):
        """Test du handler pour GET /user avec succès"""
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
        assert body['name'] == 'John Doe'
    
    @patch('index.get_user')
    def test_handler_get_user_not_found(self, mock_get_user):
        """Test du handler pour GET /user avec utilisateur non trouvé"""
        # Configuration du mock
        mock_get_user.return_value = {
            'success': False,
            'error': 'User with ID nonexistent not found'
        }
        
        event = {
            'httpMethod': 'GET',
            'path': '/user',
            'queryStringParameters': {
                'userId': 'nonexistent'
            }
        }
        context = {}
        
        response = handler(event, context)
        
        assert response['statusCode'] == 404
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'not found' in body['error'].lower()
    
    def test_handler_unsupported_method(self):
        """Test pour une méthode HTTP non supportée"""
        event = {
            'httpMethod': 'DELETE',
            'path': '/user'
        }
        context = {}
        
        response = handler(event, context)
        
        assert response['statusCode'] == 405
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'method not allowed' in body['error'].lower() 