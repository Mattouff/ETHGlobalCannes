#!/usr/bin/env python3
"""
News Agent Launcher avec logging JSON
Lance news.py et affiche les logs + écrit dans news_logs.json
"""

import subprocess
import sys
import time
import signal
import os
import json
from threading import Thread
from datetime import datetime

# Processus global pour cleanup
news_process = None

# Le fichier news_logs.json contient maintenant seulement les articles
ARTICLES_FILE = "news_logs.json"

def log_launcher_info(message: str):
    """Affiche un message du launcher sans polluer le fichier articles"""
    print(f"[LAUNCHER] {message}")

def parse_and_log_output(output_line: str):
    """Parse la sortie du News Agent pour affichage seulement (pas de logging JSON)"""
    line = output_line.strip()
    
    # Démarrage de l'agent
    if "News Agent démarré" in line:
        log_launcher_info("News Agent démarré avec succès")
    
    # Récupération automatique
    elif "Récupération automatique des news" in line:
        log_launcher_info("Début de récupération automatique des news")
    
    # Nouvelles actualités trouvées
    elif "NOUVELLES ACTUALITÉS:" in line:
        # Essayer d'extraire le nombre
        try:
            import re
            match = re.search(r'(\d+) NOUVELLES ACTUALITÉS', line)
            if match:
                count = int(match.group(1))
                log_launcher_info(f"{count} nouvelles actualités trouvées et ajoutées au JSON")
        except:
            log_launcher_info("Nouvelles actualités trouvées et ajoutées au JSON")
    
    # Appel API REST
    elif "API Call - Requête news via REST" in line:
        log_launcher_info("Requête API REST reçue")
    
    # Erreurs
    elif "ERROR" in line or "Error" in line or "error" in line:
        log_launcher_info(f"ERREUR: {line}")
    
    # Endpoints disponibles
    elif "API REST disponible" in line:
        log_launcher_info("API REST prête et accessible")

def signal_handler(sig, frame):
    """Gestionnaire pour arrêt propre avec Ctrl+C"""
    print("\n🛑 Arrêt demandé...")
    log_launcher_info("Arrêt du News Agent demandé par l'utilisateur")
    
    global news_process
    if news_process and news_process.poll() is None:
        print(f"⏹️  Arrêt du News Agent")
        news_process.terminate()
        
    # Attendre un peu avant de forcer l'arrêt
    time.sleep(2)
    
    if news_process and news_process.poll() is None:
        print(f"🔪 Force l'arrêt du News Agent")
        news_process.kill()
    
    log_launcher_info("News Agent arrêté proprement")
    print("✅ News Agent arrêté proprement")
    sys.exit(0)

def monitor_news_output(process):
    """Monitore la sortie du News Agent et l'affiche"""
    log_launcher_info("Démarrage du monitoring News Agent")
    
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            # Préfixer les logs avec timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] News: {output.strip()}")
            
            # Parser et afficher les événements importants
            parse_and_log_output(output)
    
    # Vérifier si le processus s'est arrêté de manière inattendue
    if process.poll() is not None and process.returncode != 0:
        error_msg = f"News Agent s'est arrêté avec le code d'erreur {process.returncode}"
        print(f"❌ {error_msg}")
        log_launcher_info(f"ERREUR: {error_msg}")

def main():
    """Lance seulement le News Agent avec monitoring et logging JSON"""
    
    # Gérer Ctrl+C proprement
    signal.signal(signal.SIGINT, signal_handler)
    
    print("📰 Lancement du News Agent IntentFi...")
    print("=" * 60)
    
    # Log du démarrage du launcher
    log_launcher_info("Démarrage du News Launcher")
    
    # Vérifier que le fichier existe
    current_dir = os.path.dirname(os.path.abspath(__file__))
    news_path = os.path.join(current_dir, "news.py")
    
    if not os.path.exists(news_path):
        error_msg = f"Fichier non trouvé: {news_path}"
        print(f"❌ {error_msg}")
        log_launcher_info(f"ERREUR: {error_msg}")
        return
    
    try:
        global news_process
        
        # Lancer news.py sur port 8002 (avec affichage des logs)
        print("📰 Lancement de News Agent (port 8002) - Logs en temps réel:")
        print("-" * 60)
        
        log_launcher_info("Démarrage du processus News Agent")
        
        news_process = subprocess.Popen(
            [sys.executable, news_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )

        
        # Thread pour monitorer news (logs affichés)
        news_thread = Thread(
            target=monitor_news_output, 
            args=(news_process,),
            daemon=True
        )
        news_thread.start()
        
        print(f"\n✅ News Agent lancé avec succès!")
        log_launcher_info("News Agent lancé avec succès")
        print(f"📰 News Agent: http://localhost:8002")
        print(f"   - Health: GET http://localhost:8002/health")
        print(f"   - News: POST http://localhost:8002/news")
        print(f"📄 Logs JSON: {ARTICLES_FILE}")
        print(f"\n🔍 Monitoring des logs ci-dessous...")
        print(f"   (Utilisez Ctrl+C pour arrêter)")
        print("=" * 60)
        
        # Boucle principale - attendre que le processus se termine
        while True:
            if news_process.poll() is not None:
                error_msg = "News Agent s'est arrêté de manière inattendue"
                print(f"❌ {error_msg}")
                log_launcher_info(f"ERREUR: {error_msg}")
                break
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")
    
    finally:
        # Arrêter le processus
        if news_process and news_process.poll() is None:
            news_process.terminate()

if __name__ == "__main__":
    main()
