#!/usr/bin/env python3
"""
Script de lancement et test de l'agent IntentFi
Démarre l'agent en arrière-plan et teste les endpoints
"""

import subprocess
import time
import requests
import json
import sys
import os
import signal

def start_agent():
    """Démarre l'agent en arrière-plan"""
    print("🚀 Démarrage de l'agent IntentFi...")
    try:
        # Lancer l'agent en arrière-plan
        process = subprocess.Popen(
            [sys.executable, "intellect.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Attendre un peu pour que l'agent démarre
        print("⏳ Attente du démarrage (10 secondes)...")
        time.sleep(10)
        
        return process
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return None

def test_health():
    """Test de l'endpoint de santé"""
    try:
        print("\n🔍 Test de l'endpoint /health")
        response = requests.get("http://localhost:8001/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent en bonne santé: {data.get('status')}")
            print(f"🆔 Agent ID: {data.get('address', 'N/A')[:16]}...")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_get_json():
    """Test de l'endpoint /getJson"""
    try:
        print("\n🔍 Test de l'endpoint /getJson")
        response = requests.get("http://localhost:8001/getJson", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_articles', 0)
            print(f"✅ Articles bruts récupérés: {total}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_get_analyzed():
    """Test de l'endpoint /getAnalyzed"""
    try:
        print("\n🔍 Test de l'endpoint /getAnalyzed")
        response = requests.get("http://localhost:8001/getAnalyzed", timeout=15)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_articles', 0)
            analyzed = data.get('analyzed_articles', 0)
            print(f"✅ Articles analysés: {analyzed}/{total}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_update_analyzed():
    """Test de l'endpoint /updateAnalyzed"""
    try:
        print("\n🔍 Test de l'endpoint /updateAnalyzed")
        response = requests.post("http://localhost:8001/updateAnalyzed", json={}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_articles', 0)
            analyzed = data.get('analyzed_articles', 0)
            print(f"✅ Cache mis à jour: {analyzed}/{total} articles analysés")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("🧪 Script de test de l'agent IntentFi")
    print("=" * 50)
    
    # Démarrer l'agent
    agent_process = start_agent()
    if not agent_process:
        print("❌ Impossible de démarrer l'agent")
        return
    
    try:
        # Tests des endpoints
        tests = [
            ("Santé", test_health),
            ("Articles bruts", test_get_json),
            ("Articles analysés", test_get_analyzed),
            ("Mise à jour cache", test_update_analyzed)
        ]
        
        results = []
        for test_name, test_func in tests:
            print(f"\n📋 Test: {test_name}")
            result = test_func()
            results.append((test_name, result))
            time.sleep(2)  # Pause entre les tests
        
        # Résumé
        print("\n" + "=" * 50)
        print("📊 RÉSUMÉ DES TESTS")
        print("=" * 50)
        
        passed = 0
        for test_name, result in results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
            if result:
                passed += 1
        
        print(f"\n🎯 Résultat global: {passed}/{len(results)} tests réussis")
        
        if passed == len(results):
            print("🎉 Tous les tests sont passés ! L'agent fonctionne correctement.")
        else:
            print("⚠️ Certains tests ont échoué. Vérifiez les logs.")
            
    finally:
        # Arrêter l'agent
        print("\n🛑 Arrêt de l'agent...")
        agent_process.terminate()
        try:
            agent_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            agent_process.kill()
        print("✅ Agent arrêté")

if __name__ == "__main__":
    main()
