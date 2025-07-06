import json
import pytest
import boto3
import sys
import os

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../backend/function/siteUserHandler/src'))

from moto import mock_dynamodb

# Import de nos modules après avoir configuré le path
try:
    from index import handler
except ImportError:
    # Si l'import direct ne fonctionne pas, essayer avec le chemin complet
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "index", 
        os.path.join(os.path.dirname(__file__), '../backend/function/siteUserHandler/src/index.py')
    )
    index_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(index_module)
    handler = index_module.handler

@pytest.fixture
def dynamodb_table():
    """Fixture pour créer une table DynamoDB mockée"""
    with mock_dynamodb():
        # Définir la variable d'environnement pour la table
        os.environ['STORAGE_SITEUSERTABLE_NAME'] = 'siteUserTable'
        
        # Créer un client DynamoDB mocké
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        
        # Créer la table
        table = dynamodb.create_table(
            TableName='siteUserTable',
            KeySchema=[
                {
                    'AttributeName': 'userId',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'userId',
                    'AttributeType': 'S'
                }
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        
        yield table

class TestUserHandler:
    """Tests pour les fonctions de gestion des utilisateurs"""
    
    def test_add_user_success(self, dynamodb_table):
        """Test d'ajout d'un utilisateur avec succès"""
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
    
    def test_add_user_missing_fields(self, dynamodb_table):
        """Test d'ajout d'un utilisateur avec des champs manquants"""
        event = {
            'httpMethod': 'POST',
            'path': '/user',
            'body': json.dumps({
                'userId': 'user123'
                # Manque name et email
            })
        }
        context = {}
        
        response = handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'required fields' in body['error'].lower()
    
    def test_add_user_already_exists(self, dynamodb_table):
        """Test d'ajout d'un utilisateur qui existe déjà"""
        # Ajouter un utilisateur d'abord
        dynamodb_table.put_item(
            Item={
                'userId': 'user123',
                'name': 'Existing User',
                'email': 'existing@example.com'
            }
        )
        
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
        
        assert response['statusCode'] == 409
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'already exists' in body['error'].lower()
    
    def test_get_user_success(self, dynamodb_table):
        """Test de récupération d'un utilisateur avec succès"""
        # Ajouter un utilisateur d'abord
        dynamodb_table.put_item(
            Item={
                'userId': 'user123',
                'name': 'John Doe',
                'email': 'john@example.com'
            }
        )
        
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
        assert body['email'] == 'john@example.com'
    
    def test_get_user_not_found(self, dynamodb_table):
        """Test de récupération d'un utilisateur qui n'existe pas"""
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
    
    def test_get_user_missing_userid(self, dynamodb_table):
        """Test de récupération sans userId"""
        event = {
            'httpMethod': 'GET',
            'path': '/user',
            'queryStringParameters': None
        }
        context = {}
        
        response = handler(event, context)
        
        assert response['statusCode'] == 400
        body = json.loads(response['body'])
        assert 'error' in body
        assert 'userid' in body['error'].lower()
    
    def test_unsupported_method(self, dynamodb_table):
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