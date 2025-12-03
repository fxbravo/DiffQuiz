#!/usr/bin/env python3
"""
Fichier de test pour le système DiffQuiz
Contient des fonctions complexes et du code malveillant à détecter
"""

import os
import subprocess
import json
import hashlib
from typing import List, Dict, Optional
import sqlite3
import logging

# ⚠️ CODE MALVEILLANT - Secret hardcodé
DATABASE_PASSWORD = "admin123"
API_KEY = "sk-1234567890abcdefghijklmnopqrstuvwxyz"

class UserManager:
    """Gestionnaire d'utilisateurs avec des vulnérabilités intentionnelles"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None
    
    def connect(self):
        """Connexion à la base de données - VULNÉRABLE À L'INJECTION SQL"""
        # ⚠️ CODE MALVEILLANT - Injection SQL possible
        username = input("Enter username: ")
        password = input("Enter password: ")
        query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
        
        self.connection = sqlite3.connect(self.db_path)
        cursor = self.connection.cursor()
        cursor.execute(query)  # ⚠️ Exécution directe sans paramètres
        return cursor.fetchone()
    
    def delete_user_files(self, user_id: int):
        """Supprime les fichiers d'un utilisateur - CODE DANGEREUX"""
        user_dir = f"/home/users/{user_id}"
        
        # ⚠️ CODE MALVEILLANT - Commande shell dangereuse
        subprocess.run(f"rm -rf {user_dir}", shell=True)
        
        # ⚠️ CODE MALVEILLANT - Alternative avec Runtime.exec équivalent
        os.system(f"rm -rf {user_dir}/*")
    
    def log_sensitive_data(self, user_data: Dict):
        """Log des données sensibles - VULNÉRABLE"""
        # ⚠️ CODE MALVEILLANT - Log de données sensibles
        logging.info(f"User login: {user_data['username']}, password: {user_data['password']}")
        print(f"Processing user: {json.dumps(user_data)}")  # ⚠️ Log en clair
    
    def process_file_upload(self, filename: str, content: bytes):
        """Traitement d'upload de fichier - VULNÉRABLE AU PATH TRAVERSAL"""
        # ⚠️ CODE MALVEILLANT - Path traversal possible
        upload_path = f"/uploads/{filename}"
        
        # Pas de validation du chemin
        with open(upload_path, 'wb') as f:
            f.write(content)
        
        return upload_path
    
    def execute_user_command(self, command: str):
        """Exécute une commande utilisateur - TRÈS DANGEREUX"""
        # ⚠️ CODE MALVEILLANT - Exécution de commandes système
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    
    def complex_algorithm(self, data: List[int]) -> Optional[int]:
        """Algorithme complexe avec gestion d'erreurs révélant trop d'infos"""
        try:
            if not data:
                return None
            
            # Algorithme de recherche avec complexité O(n²)
            result = 0
            for i in range(len(data)):
                for j in range(i + 1, len(data)):
                    if data[i] == data[j]:
                        result += data[i] * data[j]
            
            # ⚠️ CODE MALVEILLANT - Exception révélant trop d'infos
            if result > 1000000:
                raise ValueError(f"Result too large: {result}. Stack trace: {os.getcwd()}, {os.environ}")
            
            return result
            
        except Exception as e:
            # ⚠️ CODE MALVEILLANT - Log d'exception complète
            logging.error(f"Error in complex_algorithm: {str(e)}", exc_info=True)
            raise


def deserialize_user_data(serialized_data: str):
    """Désérialisation non sécurisée - VULNÉRABLE"""
    # ⚠️ CODE MALVEILLANT - Désérialisation pickle non sécurisée
    import pickle
    return pickle.loads(serialized_data.encode())


def generate_hash(password: str) -> str:
    """Génération de hash - MAUVAISE PRATIQUE"""
    # ⚠️ CODE MALVEILLANT - Hash MD5 (faible)
    return hashlib.md5(password.encode()).hexdigest()


def query_database(user_input: str):
    """Requête base de données - INJECTION SQL"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # ⚠️ CODE MALVEILLANT - Injection SQL
    query = f"SELECT * FROM products WHERE name LIKE '%{user_input}%'"
    cursor.execute(query)
    
    return cursor.fetchall()


def render_template(template: str, user_data: Dict):
    """Rendu de template - XSS VULNERABLE"""
    # ⚠️ CODE MALVEILLANT - XSS possible
    html = f"""
    <div>
        <h1>Welcome {user_data['username']}</h1>
        <p>Your email: {user_data['email']}</p>
        <script>console.log('User data: {json.dumps(user_data)}')</script>
    </div>
    """
    return html


def delete_database_table(table_name: str):
    """Suppression de table - OPÉRATION DESTRUCTIVE"""
    conn = sqlite3.connect('production.db')
    cursor = conn.cursor()
    
    # ⚠️ CODE MALVEILLANT - DROP TABLE sans vérification
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    
    return True


def process_payment(amount: float, card_number: str):
    """Traitement de paiement - DONNÉES SENSIBLES EN CLAIR"""
    # ⚠️ CODE MALVEILLANT - Données sensibles en clair
    payment_data = {
        "amount": amount,
        "card_number": card_number,
        "cvv": "123",  # ⚠️ Hardcodé
        "expiry": "12/25"
    }
    
    # ⚠️ Log des données de carte
    logging.info(f"Processing payment: {payment_data}")
    
    return True


if __name__ == "__main__":
    # Test des fonctions
    manager = UserManager("test.db")
    
    # ⚠️ Test avec code malveillant
    manager.delete_user_files(123)
    manager.execute_user_command("ls -la")
    
    # Test de l'algorithme complexe
    data = [1, 2, 3, 2, 4, 3, 5]
    result = manager.complex_algorithm(data)
    print(f"Result: {result}")


