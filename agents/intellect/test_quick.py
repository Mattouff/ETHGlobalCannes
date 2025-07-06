#!/usr/bin/env python3
"""
Script de test rapide pour l'agent IntentFi
Test des endpoints avec les 2 articles existants
"""

import requests
import json
import time

BASE_URL = "http://localhost:8001"

def test_health():
    """Test de l'endpoint de santé"""
    print("🔍 Test de l'endpoint /health")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Agent en bonne santé: {data.get('status')}")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_get_json():
    """Test de l'endpoint /getJson"""
    print("\n🔍 Test de l'endpoint /getJson (articles bruts)")
    try:
        response = requests.get(f"{BASE_URL}/getJson", timeout=10)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_articles', 0)
            print(f"✅ Articles bruts récupérés: {total}")
            if total > 0:
                print(f"📰 Premier article: {data['articles'][0]['title'][:50]}...")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def test_fallback_analysis():
    """Test du fallback d'analyse par mots-clés"""
    print("\n🔍 Test de l'endpoint /getJsonDetails (analyse temps réel avec fallback)")
    try:
        response = requests.get(f"{BASE_URL}/getJsonDetails", timeout=60)
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_articles', 0)
            analyzed = data.get('analyzed_articles', 0)
            print(f"✅ Articles analysés: {analyzed}/{total}")
            
            if total > 0:
                first_article = data['articles'][0]
                print(f"📰 Premier article: {first_article['title'][:50]}...")
                print(f"📊 Rate: {first_article.get('rate', 'N/A')}")
                print(f"📝 Review: {first_article.get('review', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ Erreur HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

def main():
    print("🧪 Test rapide de l'agent IntentFi avec les articles existants")
    print("=" * 60)
    
    # Tests des endpoints
    tests = [
        ("Santé de l'agent", test_health),
        ("Articles bruts", test_get_json),
        ("Analyse temps réel", test_fallback_analysis)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Test: {test_name}")
        result = test_func()
        results.append((test_name, result))
        if not result:
            print("⚠️ Arrêt des tests après échec")
            break
        time.sleep(1)  # Pause entre les tests
    
    # Résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Résultat: {passed}/{len(results)} tests réussis")
    
    if passed == len(results):
        print("🎉 Tous les tests sont passés ! L'analyse des articles fonctionne.")
    else:
        print("⚠️ Certains tests ont échoué.")

if __name__ == "__main__":
    main()
