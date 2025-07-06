#!/usr/bin/env python3
import requests
import json

# Test de l'endpoint de recommandation trading
url = "http://localhost:8000/trading/recommend"
headers = {"Content-Type": "application/json"}

# Test pour chaque token autorisé
tokens = ["ETH", "ARBITRUM", "FLOW", "OPTI"]

for token in tokens:
    print(f"\n{'='*50}")
    print(f"Test de recommandation pour {token}")
    print(f"{'='*50}")
    
    payload = {"token_symbol": token}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Succès: {data.get('success', False)}")
            print(f"Message: {data.get('message', 'N/A')}")
            
            if 'analysis' in data and data['analysis']:
                analysis = data['analysis']
                print(f"Recommandation: {analysis.get('recommendation', 'N/A')}")
                print(f"Confiance: {analysis.get('confidence', 0):.2%}")
                print(f"Sentiment: {analysis.get('news_sentiment', 'N/A')}")
                print(f"Raisonnement: {analysis.get('reasoning', 'N/A')[:100]}...")
            else:
                print("Aucune analyse disponible")
        else:
            print(f"Erreur: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion: {e}")
    except Exception as e:
        print(f"Erreur: {e}")

print(f"\n{'='*50}")
print("Tests terminés")
print(f"{'='*50}")

# Test avec un token suspect pour vérifier le SELL automatique
suspect_tokens = ["RareTron.io", "SafeMoonInu", "BabyDoge"]

print(f"\n{'='*60}")
print("TESTS DE TOKENS SUSPECTS (devrait retourner SELL automatique)")
print(f"{'='*60}")

for token in suspect_tokens:
    print(f"\n{'='*50}")
    print(f"Test de recommandation pour {token} (SUSPECT)")
    print(f"{'='*50}")
    
    payload = {"token_symbol": token}
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Succès: {data.get('success', False)}")
            print(f"Message: {data.get('message', 'N/A')}")
            
            if 'analysis' in data and data['analysis']:
                analysis = data['analysis']
                print(f"Recommandation: {analysis.get('recommendation', 'N/A')}")
                print(f"Confiance: {analysis.get('confidence', 0):.2%}")
                print(f"Sentiment: {analysis.get('news_sentiment', 'N/A')}")
                print(f"Raisonnement: {analysis.get('reasoning', 'N/A')[:100]}...")
                
                # Vérifier que c'est bien un SELL automatique
                if analysis.get('recommendation') == 'sell' and analysis.get('confidence', 0) > 0.9:
                    print("✅ SELL automatique détecté correctement!")
                else:
                    print("❌ Erreur: devrait être SELL automatique avec haute confiance")
            else:
                print("Aucune analyse disponible")
        else:
            print(f"Erreur: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Erreur de connexion: {e}")
    except Exception as e:
        print(f"Erreur: {e}")

print(f"\n{'='*50}")
print("Tests terminés")
print(f"{'='*50}")
