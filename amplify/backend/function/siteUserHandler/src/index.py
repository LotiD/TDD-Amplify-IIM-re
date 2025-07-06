import json
import os
from user_service import add_user, get_user

def handler(event, context):
    """
    Handler principal pour les opérations sur les utilisateurs
    
    Supporte:
    - POST /user : Créer un nouvel utilisateur  
    - GET /user?userId=XXX : Récupérer un utilisateur
    """
    print('received event:')
    print(json.dumps(event))
    
    # Headers CORS
    headers = {
        'Access-Control-Allow-Headers': '*',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'OPTIONS,POST,GET',
        'Content-Type': 'application/json'
    }
    
    try:
        http_method = event.get('httpMethod')
        path = event.get('path', '')
        
        # Route POST /user - Créer un utilisateur
        if http_method == 'POST' and '/user' in path:
            return handle_add_user(event, headers)
        
        # Route GET /user - Récupérer un utilisateur
        elif http_method == 'GET' and '/user' in path:
            return handle_get_user(event, headers)
        
        # Route OPTIONS - Support CORS
        elif http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps({'message': 'CORS preflight'})
            }
        
        # Méthode non supportée
        else:
            return {
                'statusCode': 405,
                'headers': headers,
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        print(f'Error in handler: {str(e)}')
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_add_user(event, headers):
    """Gère la création d'un utilisateur"""
    try:
        # Parser le body de la requête
        if not event.get('body'):
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        user_data = json.loads(event['body'])
        
        # Appeler le service
        result = add_user(user_data)
        
        if result['success']:
            return {
                'statusCode': 201,
                'headers': headers,
                'body': json.dumps({
                    'message': result['message'],
                    'userId': result['userId']
                })
            }
        else:
            # Déterminer le code d'erreur approprié
            if 'already exists' in result['error']:
                status_code = 409  # Conflict
            elif 'required fields' in result['error']:
                status_code = 400  # Bad Request
            else:
                status_code = 500  # Internal Server Error
            
            return {
                'statusCode': status_code,
                'headers': headers,
                'body': json.dumps({'error': result['error']})
            }
            
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        print(f'Error in handle_add_user: {str(e)}')
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_get_user(event, headers):
    """Gère la récupération d'un utilisateur"""
    try:
        # Récupérer le userId depuis les query parameters
        query_params = event.get('queryStringParameters') or {}
        user_id = query_params.get('userId')
        
        if not user_id:
            return {
                'statusCode': 400,
                'headers': headers,
                'body': json.dumps({'error': 'UserId parameter is required'})
            }
        
        # Appeler le service
        result = get_user(user_id)
        
        if result['success']:
            return {
                'statusCode': 200,
                'headers': headers,
                'body': json.dumps(result['user'])
            }
        else:
            # Déterminer le code d'erreur approprié
            if 'not found' in result['error']:
                status_code = 404  # Not Found
            elif 'required' in result['error']:
                status_code = 400  # Bad Request
            else:
                status_code = 500  # Internal Server Error
            
            return {
                'statusCode': status_code,
                'headers': headers,
                'body': json.dumps({'error': result['error']})
            }
            
    except Exception as e:
        print(f'Error in handle_get_user: {str(e)}')
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': 'Internal server error'})
        }