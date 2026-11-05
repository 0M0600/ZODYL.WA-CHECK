import os
import asyncio
from playwright.async_api import async_playwright

class WhatsAppClient:
    def __init__(self, session_id: str, proxy: dict = None):
        """
        Initialise le module de vérification (Partie 3).
        Permet l'injection d'un proxy (Partie 4) et d'un ID de session unique.
        """
        self.session_id = session_id
        self.proxy = proxy
        self.session_dir = f"./sessions/{session_id}"
        os.makedirs(self.session_dir, exist_ok=True)

    async def verify_number_status(self, phone_number: str) -> str:
        """
        Émule un client pour interroger les serveurs de messagerie
        et déterminer le statut exact d'un compte.
        """
        async with async_playwright() as p:
            # Configuration du navigateur avec l'empreinte et le proxy éventuel
            browser_args = [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox"
            ]

            # Lancement d'un contexte de navigation persistant (gère le cache des sessions)
            context = await p.chromium.launch_persistent_context(
                user_data_dir=self.session_dir,
                headless=True,  # True pour tourner en arrière-plan sur Kali
                args=browser_args,
                proxy=self.proxy
            )

            page = await context.new_page()

            # Utilisation de l'API web d'acheminement officielle pour initialiser la session
            target_url = f"https://whatsapp.com{phone_number}&text=&type=phone_number&app_absent=1"

            try:
                await page.goto(target_url, timeout=30000)

                # Émulation du temps d'attente pour le chargement des protocoles internes
                await asyncio.sleep(5)

                # Analyse des éléments du DOM (Sélecteurs CSS) pour déterminer le statut
                # Si une boîte de dialogue d'erreur apparaît : le numéro n'existe pas
                invalid_selectors = [
                    "text=Le numéro de téléphone partagé via une URL est invalide",
                    "text=Phone number shared via url is invalid",
                    "div[data-animate-modal-popup]"
                ]

                for selector in invalid_selectors:
                    if await page.locator(selector).is_visible():
                        await context.close()
                        return "unknown_or_inactive"

                # Si la zone de saisie du message s'affiche : le numéro est actif
                if await page.locator("div[contenteditable='true']").is_visible():
                    await context.close()
                    return "active"

                await context.close()
                return "unknown"

            except Exception as e:
                await context.close()
                # Log d'erreur standard pour le debugging d'infrastructure
                print(f"[-] Erreur réseau ou timeout lors de l'émulation : {str(e)}")
                return "network_timeout"

# Bloc de test unitaire pour valider le composant de manière isolée
if __name__ == "__main__":
    async def run_test():
        # Exemple d'appel : ID de session 001, sans proxy pour le test local
        client = WhatsAppClient(session_id="session_001")
        print("[*] Lancement de la vérification du module d'émulation...")
        status = await client.verify_number_status("+243841433663")
        print(f"[+] Résultat de l'analyse du protocole : {status}")

    asyncio.run(run_test())



