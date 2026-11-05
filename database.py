import sqlite3
import time

class AuditDatabase:
    def __init__(self, db_name="audit_cache.db"):
        """
        Initialise la persistance et la gestion du cache (Partie 5).
        Crée la table SQLite sous les standards d'indexation relationnelle.
        """
        self.db_name = db_name
        self.cache_ttl_seconds = 86400  # Rétention du cache : 24 heures
        self._bootstrap_db()

    def _bootstrap_db(self):
        """Crée la structure de la table si elle n'existe pas avec un index unique."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS phone_audits (
                    number TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    last_checked REAL NOT NULL
                )
            """)
            # Indexation pour accélérer les requêtes de recherche à grande échelle
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_numbers ON phone_audits(number)")
            conn.commit()

    def get_cached_status(self, number: str) -> str:
        """
        Interroge la couche de cache persistante.
        Vérifie la fraîcheur de la donnée (Time-To-Live).
        """
        current_time = time.time()
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT status, last_checked FROM phone_audits WHERE number = ?", (number,))
            row = cursor.fetchone()

            if row:
                status, last_checked = row
                # Vérification de l'expiration du cache (TTL)
                if current_time - last_checked < self.cache_ttl_seconds:
                    return status  # La donnée est fraîche, on la renvoie directement
                else:
                    print(f"[i] Cache expiré pour le numéro : {number}")
            return None  # La donnée n'est pas en cache ou est trop ancienne

    def save_to_cache(self, number: str, status: str):
        """Enregistre ou met à jour le statut d'un numéro audité avec un timestamp précis."""
        current_time = time.time()
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO phone_audits (number, status, last_checked)
                VALUES (?, ?, ?)
            """, (number, status, current_time))
            conn.commit()

# Bloc de test unitaire pour valider la brique de stockage
if __name__ == "__main__":
    db = AuditDatabase()
    test_num = "+243841433663"

    print("[*] Étape 1 : Vérification d'un numéro non répertorié...")
    print(f"Statut en cache : {db.get_cached_status(test_num)}")  # Devrait afficher None

    print("\n[*] Étape 2 : Écriture dans la base de données (Statut: active)...")
    db.save_to_cache(test_num, "active")

    print("\n[*] Étape 3 : Nouvelle vérification immédiate du cache...")
    print(f"Statut récupéré (Fraîcheur OK) : {db.get_cached_status(test_num)}")  # Devrait afficher 'active'



