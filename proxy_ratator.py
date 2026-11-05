import random
from collections import deque

class ProxyRotator:
    def __init__(self):
        """
        Initialise le pool de proxys et d'empreintes de navigateurs (Partie 4).
        Utilise une file doublement terminée (deque) pour effectuer une rotation circulaire.
        """
        # Intégration de ta configuration de nœud réseau avec ton identifiant unique
        self.proxys = deque([
            {
                "server": "http://127.0.0.1:8080",
                "username": "243841433663",
                "password": "session_auth_token"
            },
            {"server": "http://example.com", "username": "user2", "password": "pass2"},
            {"server": "http://example.com", "username": "user3", "password": "pass3"},
        ])

        # Liste d'User-Agents récents et réalistes pour simuler différents appareils
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]

    def get_next_routing_node(self) -> tuple[dict, str]:
        """
        Effectue une rotation de type Round-Robin pour le proxy,
        et sélectionne aléatoirement un User-Agent.
        """
        if not self.proxys:
            return None, random.choice(self.user_agents)

        # Extraction du premier proxy de la file
        current_proxy = self.proxys.popleft()

        # Réinsertion à la fin de la file pour assurer la rotation circulaire (Round-Robin)
        self.proxys.append(current_proxy)

        # Sélection aléatoire d'un profil de navigateur
        current_ua = random.choice(self.user_agents)

        return current_proxy, current_ua

    def report_failed_proxy(self, proxy: dict):
        """
        Si un proxy échoue ou subit un timeout réseau, cette méthode permet
        de le retirer du pool actif pour préserver la qualité du routage.
        """
        if proxy in self.proxys:
            self.proxys.remove(proxy)
            print(f"[!] Proxy compromis retiré du pool actif : {proxy['server']}")

# Bloc de test pour valider le composant
if __name__ == "__main__":
    rotator = ProxyRotator()
    print("[*] Test de la cinématique de rotation (Round-Robin) :")
    for i in range(4):
        proxy, ua = rotator.get_next_routing_node()
        print(f"Requête #{i+1} -> Proxy Server: {proxy['server']} | User: {proxy['username']} | UA: {ua[:30]}...")



