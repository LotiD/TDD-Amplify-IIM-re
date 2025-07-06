import sys
import os
from unittest.mock import Mock, patch

# Ajouter le répertoire src au PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'amplify/backend/function/siteUserHandler/src'))

# Variables d'environnement pour les tests
os.environ['STORAGE_SITEUSERTABLE_NAME'] = 'siteUserTable'

from user_service import add_user, get_user

def demo_mock_detaille():
    """Démonstration détaillée d'un mock"""
    print("🎭 DÉMONSTRATION DU MOCK")
    print("=" * 50)
    
    print("\n1️⃣ AVANT LE MOCK:")
    print("   La fonction add_user() essaierait d'utiliser DynamoDB")
    
    print("\n2️⃣ CRÉATION DU MOCK:")
    with patch('user_service.get_dynamodb_table') as mock_get_table:
        
        # On crée un faux objet "table"
        fake_table = Mock()
        print(f"   ✅ fake_table créé: {fake_table}")
        
        # On configure ce que le faux objet doit retourner
        fake_table.get_item.return_value = {}
        fake_table.put_item.return_value = {}
        print("   ✅ fake_table configuré pour retourner {} pour get_item et put_item")
        
        # On dit à notre mock de retourner notre faux objet
        mock_get_table.return_value = fake_table
        print("   ✅ mock_get_table configuré pour retourner fake_table")
        
        print("\n3️⃣ APPEL DE LA FONCTION:")
        user_data = {
            'userId': 'demo123',
            'name': 'Demo User',
            'email': 'demo@example.com'
        }
        
        print(f"   📤 Appel de add_user avec: {user_data}")
        
        # Maintenant quand add_user() appelle get_dynamodb_table():
        # → elle reçoit notre fake_table
        # → fake_table.get_item() retourne {}
        # → fake_table.put_item() retourne {}
        result = add_user(user_data)
        
        print(f"   📥 Résultat reçu: {result}")
        
        print("\n4️⃣ CE QUI S'EST PASSÉ EN INTERNE:")
        print("   ↪️ add_user() a appelé get_dynamodb_table()")
        print("   ↪️ get_dynamodb_table() a retourné fake_table (pas DynamoDB !)")
        print("   ↪️ fake_table.get_item() a retourné {} (utilisateur inexistant)")
        print("   ↪️ fake_table.put_item() a retourné {} (insertion simulée)")
        print("   ↪️ add_user() a retourné success: True")

def demo_mock_vs_reel():
    """Comparaison Mock vs Réel"""
    print("\n🆚 COMPARAISON MOCK VS RÉEL")
    print("=" * 50)
    
    print("\n❌ SANS MOCK (ce qui se passerait):")
    print("   1. get_dynamodb_table() → Connexion AWS")
    print("   2. boto3.resource('dynamodb') → Authentification AWS") 
    print("   3. table.get_item() → Requête réseau vers DynamoDB")
    print("   4. table.put_item() → Requête réseau vers DynamoDB")
    print("   ⚠️  Problèmes: lent, coûteux, nécessite AWS configuré")
    
    print("\n✅ AVEC MOCK (ce qui se passe réellement):")
    print("   1. get_dynamodb_table() → Retourne fake_table")
    print("   2. fake_table.get_item() → Retourne {} instantanément")
    print("   3. fake_table.put_item() → Retourne {} instantanément")
    print("   🎯 Avantages: rapide, gratuit, fonctionne partout")

def demo_configuration_mock():
    """Démonstration de différentes configurations de mock"""
    print("\n⚙️ CONFIGURATIONS DE MOCK")
    print("=" * 50)
    
    # Configuration 1: Utilisateur n'existe pas
    print("\n📝 Scénario 1: Utilisateur n'existe pas")
    with patch('user_service.get_dynamodb_table') as mock_get_table:
        fake_table = Mock()
        fake_table.get_item.return_value = {}  # Pas d'Item = utilisateur inexistant
        mock_get_table.return_value = fake_table
        
        result = add_user({'userId': 'new123', 'name': 'New', 'email': 'new@test.com'})
        print(f"   Résultat: {result['success']} - {result.get('message', result.get('error'))}")
    
    # Configuration 2: Utilisateur existe déjà
    print("\n📝 Scénario 2: Utilisateur existe déjà")
    with patch('user_service.get_dynamodb_table') as mock_get_table:
        fake_table = Mock()
        fake_table.get_item.return_value = {
            'Item': {'userId': 'existing123', 'name': 'Existing User'}
        }  # Item présent = utilisateur existe
        mock_get_table.return_value = fake_table
        
        result = add_user({'userId': 'existing123', 'name': 'New', 'email': 'new@test.com'})
        print(f"   Résultat: {result['success']} - {result['error']}")

if __name__ == '__main__':
    demo_mock_detaille()
    demo_mock_vs_reel() 
    demo_configuration_mock()
    
    print("\n🎉 Voilà comment fonctionnent les mocks !")
    print("Les mocks permettent de tester la logique sans les dépendances externes.") 