import boto3
import os
from botocore.exceptions import ClientError

# Configuration de DynamoDB
TABLE_NAME = os.environ.get('STORAGE_SITEUSERTABLE_NAME', 'siteUserTable')

def get_dynamodb_table():
    """
    Retourne la table DynamoDB. Crée la connexion à la demande.
    """
    dynamodb = boto3.resource('dynamodb')
    return dynamodb.Table(TABLE_NAME)

def add_user(user_data):
    """
    Ajoute un nouvel utilisateur dans DynamoDB
    
    Args:
        user_data (dict): Données de l'utilisateur avec userId, name, email
        
    Returns:
        dict: Résultat de l'opération avec success (bool) et message/error
    """
    # Vérifier les champs requis
    required_fields = ['userId', 'name', 'email']
    missing_fields = [field for field in required_fields if not user_data.get(field)]
    
    if missing_fields:
        return {
            'success': False,
            'error': f'Missing required fields: {", ".join(missing_fields)}'
        }
    
    try:
        table = get_dynamodb_table()
        
        # Vérifier si l'utilisateur existe déjà
        response = table.get_item(Key={'userId': user_data['userId']})
        
        if 'Item' in response:
            return {
                'success': False,
                'error': f'User with ID {user_data["userId"]} already exists'
            }
        
        # Ajouter l'utilisateur
        table.put_item(Item=user_data)
        
        return {
            'success': True,
            'message': 'User created successfully',
            'userId': user_data['userId']
        }
        
    except ClientError as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        }

def get_user(user_id):
    """
    Récupère un utilisateur depuis DynamoDB
    
    Args:
        user_id (str): ID de l'utilisateur à récupérer
        
    Returns:
        dict: Résultat de l'opération avec success (bool) et user/error
    """
    if not user_id:
        return {
            'success': False,
            'error': 'UserId is required'
        }
    
    try:
        table = get_dynamodb_table()
        response = table.get_item(Key={'userId': user_id})
        
        if 'Item' not in response:
            return {
                'success': False,
                'error': f'User with ID {user_id} not found'
            }
        
        return {
            'success': True,
            'user': response['Item']
        }
        
    except ClientError as e:
        return {
            'success': False,
            'error': f'Database error: {str(e)}'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f'Unexpected error: {str(e)}'
        } 