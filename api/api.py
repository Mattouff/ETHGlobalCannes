import os
import requests
import redis
import json
import asyncio
import time
from datetime import datetime, timedelta
from fastapi import FastAPI, Query, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, List

load_dotenv()

API_KEY = os.getenv("API_FOOTBALL_KEY", "8582cd3b0ffe1e7ec082142c90f0ab92")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

# Configuration Redis optimisée
rdb = redis.Redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=5, socket_timeout=5)

app = FastAPI(title="Football Results API", version="1.0")

def get_date_range():
    """Retourne les dates pour hier, aujourd'hui et demain"""
    today = datetime.utcnow()
    yesterday = (today - timedelta(days=1)).strftime("%Y-%m-%d")
    today_str = today.strftime("%Y-%m-%d")
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    return yesterday, today_str, tomorrow

def test_redis_connection():
    """Test la connexion Redis"""
    try:
        rdb.ping()
        print("[✓] Redis connection OK")
        return True
    except Exception as e:
        print(f"[✗] Redis connection failed: {e}")
        return False

def fetch_football_data(date: str, status: str) -> List[Dict]:
    """Fetch les données football pour une date et un statut donnés"""
    headers = {"x-apisports-key": API_KEY}
    url = f"https://v3.football.api-sports.io/fixtures?status={status}&date={date}"
    
    try:
        print(f"[API] Fetching {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get("response", [])
            print(f"[✓] Fetched {len(fixtures)} fixtures for {date} ({status})")
            return fixtures
        else:
            print(f"[✗] API Error {response.status_code}: {response.text}")
            return []
            
    except Exception as e:
        print(f"[✗] Error fetching {url}: {e}")
        return []

def store_fixtures_batch(fixtures: List[Dict]):
    """Stocke les fixtures en batch avec pipeline Redis"""
    if not fixtures:
        print("[INFO] No fixtures to store")
        return 0
    
    print(f"[INFO] Starting to process {len(fixtures)} fixtures")
    
    pipe = rdb.pipeline()
    stored_count = 0
    error_count = 0
    
    for i, fixture in enumerate(fixtures):
        try:
            # Debug: log pour les 3 premières fixtures
            if i < 3:
                print(f"[DEBUG] Fixture {i} keys: {list(fixture.keys()) if isinstance(fixture, dict) else 'Not a dict'}")
            
            # Vérification de la structure
            if not isinstance(fixture, dict) or "fixture" not in fixture:
                print(f"[✗] Invalid fixture structure at index {i}: {type(fixture)}")
                error_count += 1
                continue
                
            f = fixture["fixture"]
            l = fixture["league"]
            t = fixture["teams"]
            g = fixture["goals"]
            status = f["status"]
            
            # Debug: log pour les 3 premières fixtures
            if i < 3:
                print(f"[DEBUG] Fixture {i} - ID: {f.get('id')}, Date: {f.get('date')}, Status: {status.get('short')}")
            
            # Vérifications supplémentaires
            if not f.get("id") or not f.get("date"):
                print(f"[✗] Missing required fields in fixture {i}: id={f.get('id')}, date={f.get('date')}")
                error_count += 1
                continue
            
            # Données de base
            result_id = str(f["id"])
            home = t["home"]["name"]
            away = t["away"]["name"]
            home_score = g["home"] if g["home"] is not None else 0
            away_score = g["away"] if g["away"] is not None else 0
            
            # Calcul du gagnant
            winner = ""
            if status["short"] == "FT" and home_score != away_score:
                winner = home if home_score > away_score else away
            elif status["short"] == "FT":
                winner = "Draw"
            
            # Clé Redis structurée
            redis_key = f"football:{f['date']}:{result_id}"
            
            # Normalisation de la date : extraire seulement YYYY-MM-DD
            fixture_date = f["date"]
            if "T" in fixture_date:
                fixture_date = fixture_date.split("T")[0]  # 2025-07-10T00:00:00+00:00 -> 2025-07-10
            
            # Données structurées - avec nettoyage des valeurs None
            fixture_data = {
                "id": result_id,
                "sport": "football",
                "date": fixture_date,  # Date normalisée
                "timestamp": str(f.get("timestamp", 0)),
                "league_id": str(l["id"]),
                "league": l["name"] or "",
                "country": l.get("country", "") or "",
                "home_team": home,
                "away_team": away,
                "home_score": str(home_score),
                "away_score": str(away_score),
                "status": status["short"],
                "status_long": status.get("long", "") or "",
                "winner": winner,
                "home_logo": t["home"].get("logo", "") or "",
                "away_logo": t["away"].get("logo", "") or "",
                "venue": f.get("venue", {}).get("name", "") or "",
                "referee": f.get("referee", "") or "",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Nettoyage final : convertir toutes les valeurs None en string vide
            for key, value in fixture_data.items():
                if value is None:
                    fixture_data[key] = ""
            
            # Stockage avec la date normalisée
            redis_key = f"football:{fixture_date}:{result_id}"
            
            # Stockage
            pipe.hset(redis_key, mapping=fixture_data)
            # Index par date pour un accès rapide (utilise la date normalisée)
            pipe.sadd(f"index:date:{fixture_date}", redis_key)
            # Index par ligue
            pipe.sadd(f"index:league:{l['id']}", redis_key)
            # Index par statut
            pipe.sadd(f"index:status:{status['short']}", redis_key)
            
            stored_count += 1
            
            # Log de progression tous les 100 items
            if stored_count % 100 == 0:
                print(f"[INFO] Processed {stored_count}/{len(fixtures)} fixtures")
            
        except KeyError as e:
            print(f"[✗] Missing key in fixture {i}: {e}")
            print(f"[DEBUG] Fixture structure: {list(fixture.keys()) if isinstance(fixture, dict) else 'Not a dict'}")
            error_count += 1
        except Exception as e:
            print(f"[✗] Error processing fixture {i}: {e}")
            print(f"[DEBUG] Fixture: {fixture}")
            error_count += 1
    
    # Exécution du pipeline
    if stored_count > 0:
        try:
            print(f"[INFO] Executing Redis pipeline with {stored_count} operations...")
            pipe.execute()
            print(f"[✓] Stored {stored_count} fixtures in Redis (errors: {error_count})")
            return stored_count
        except Exception as e:
            print(f"[✗] Redis pipeline error: {e}")
            return 0
    else:
        print(f"[✗] No fixtures to store (errors: {error_count})")
        return 0

def cleanup_old_data():
    """Nettoie les anciennes données (garde seulement hier, aujourd'hui, demain)"""
    yesterday, today, tomorrow = get_date_range()
    valid_dates = {yesterday, today, tomorrow}
    
    try:
        # Récupère toutes les clés football
        all_keys = rdb.keys("football:*")
        pipe = rdb.pipeline()
        deleted_count = 0
        
        for key in all_keys:
            # Parse la date depuis la clé: football:YYYY-MM-DD:id
            try:
                date_part = key.split(":")[1]
                if date_part not in valid_dates:
                    pipe.delete(key)
                    deleted_count += 1
            except (IndexError, ValueError):
                # Clé mal formée, on la supprime
                pipe.delete(key)
                deleted_count += 1
        
        # Nettoie aussi les index anciens
        all_date_indexes = rdb.keys("index:date:*")
        for index_key in all_date_indexes:
            try:
                date_part = index_key.split(":")[2]
                if date_part not in valid_dates:
                    pipe.delete(index_key)
            except (IndexError, ValueError):
                pipe.delete(index_key)
        
        pipe.execute()
        print(f"[✓] Cleaned {deleted_count} old records")
        
    except Exception as e:
        print(f"[✗] Cleanup error: {e}")

def fetch_and_store_results():
    """Fonction principale de fetch et stockage optimisée"""
    start_time = time.time()
    print(f"[START] Fetching football results at {datetime.utcnow().isoformat()}")
    
    # Test connexion Redis
    if not test_redis_connection():
        return {"error": "Redis connection failed"}
    
    yesterday, today, tomorrow = get_date_range()
    
    # Configuration des requêtes
    fetch_configs = [
        (yesterday, "FT"),  # Matchs terminés d'hier
        (today, "NS"),      # Matchs à venir aujourd'hui
        (today, "LIVE"),    # Matchs en cours aujourd'hui  
        (today, "FT"),      # Matchs terminés aujourd'hui
        (tomorrow, "NS")    # Matchs à venir demain
    ]
    
    all_fixtures = []
    
    # Fetch en parallèle avec ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=3) as executor:
        future_to_config = {
            executor.submit(fetch_football_data, date, status): (date, status)
            for date, status in fetch_configs
        }
        
        for future in future_to_config:
            try:
                fixtures = future.result(timeout=30)
                all_fixtures.extend(fixtures)
            except Exception as e:
                date, status = future_to_config[future]
                print(f"[✗] Failed to fetch {date} {status}: {e}")
    
    # Stockage en batch
    stored_count = store_fixtures_batch(all_fixtures)
    
    # Nettoyage des anciennes données
    cleanup_old_data()
    
    # Mise à jour du timestamp
    rdb.set("last_refresh", datetime.utcnow().isoformat())
    
    duration = time.time() - start_time
    result = {
        "status": "success",
        "fetched": len(all_fixtures),
        "stored": stored_count,
        "duration": f"{duration:.2f}s",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print(f"[✓] Fetch completed: {result}")
    return result

# Configuration du scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    fetch_and_store_results, 
    "cron", 
    hour=1, 
    minute=0, 
    id="fetch_football_results"
)
scheduler.start()

# ==================== ENDPOINTS ====================

@app.on_event("startup")
async def startup_event():
    """Initialisation au démarrage"""
    print("[STARTUP] Football Results API starting...")
    if test_redis_connection():
        print("[STARTUP] Ready to serve requests")
    else:
        print("[STARTUP] Warning: Redis connection issues")

@app.get("/")
def home():
    """Page d'accueil de l'API"""
    return {
        "message": "Football Results API v1.0",
        "endpoints": {
            "fixtures": "/football/fixtures",
            "filters": "/football/filters", 
            "stats": "/stats",
            "fetch": "POST /fetch",
            "clear": "POST /clear"
        },
        "status": "running"
    }

@app.get("/health")
def health_check():
    """Vérification de santé de l'API"""
    redis_ok = test_redis_connection()
    last_refresh = rdb.get("last_refresh")
    
    return {
        "status": "healthy" if redis_ok else "degraded",
        "redis": "connected" if redis_ok else "disconnected",
        "last_refresh": last_refresh,
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/stats")
def get_stats():
    """Statistiques générales"""
    try:
        total_fixtures = len(rdb.keys("football:*"))
        yesterday, today, tomorrow = get_date_range()
        
        stats_by_date = {}
        for date in [yesterday, today, tomorrow]:
            count = len(rdb.keys(f"football:{date}:*"))
            stats_by_date[date] = count
        
        return {
            "total_fixtures": total_fixtures,
            "by_date": stats_by_date,
            "last_refresh": rdb.get("last_refresh"),
            "date_range": {
                "yesterday": yesterday,
                "today": today, 
                "tomorrow": tomorrow
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")

@app.post("/fetch")
def manual_fetch():
    """Fetch manuel des résultats"""
    try:
        result = fetch_and_store_results()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fetch error: {str(e)}")

@app.post("/clear")
def clear_all_data():
    """Vide toutes les données football"""
    try:
        # Supprime toutes les clés football et index
        keys_to_delete = []
        keys_to_delete.extend(rdb.keys("football:*"))
        keys_to_delete.extend(rdb.keys("index:*"))
        
        if keys_to_delete:
            rdb.delete(*keys_to_delete)
        
        return {
            "status": "success",
            "deleted": len(keys_to_delete),
            "message": "All football data cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Clear error: {str(e)}")

@app.get("/football/fixtures")
def get_football_fixtures(
    page: int = Query(1, ge=1, description="Numéro de page (>=1)"),
    page_size: int = Query(20, ge=1, le=100, description="Taille de page (1-100)"),
    status: Optional[str] = Query(None, description="Statut: FT, NS, LIVE, ALL"),
    league: Optional[str] = Query(None, description="Nom ou ID de ligue"),
    date: Optional[str] = Query(None, description="Date YYYY-MM-DD"),
    country: Optional[str] = Query(None, description="Pays")
):
    """
    Récupère les fixtures de football avec filtres et pagination optimisés
    """
    try:
        start_time = time.time()
        
        # Construction de la requête de base
        if date:
            # Recherche par date spécifique
            base_keys = list(rdb.smembers(f"index:date:{date}"))
            if not base_keys:
                base_keys = rdb.keys(f"football:{date}:*")
        else:
            # Toutes les fixtures des 3 jours
            yesterday, today, tomorrow = get_date_range()
            base_keys = []
            for d in [yesterday, today, tomorrow]:
                date_keys = list(rdb.smembers(f"index:date:{d}"))
                if not date_keys:
                    date_keys = rdb.keys(f"football:{d}:*")
                base_keys.extend(date_keys)
        
        # Filtrage optimisé
        filtered_keys = []
        
        if status and status != "ALL":
            # Utilise l'index de statut si possible
            status_keys = set(rdb.smembers(f"index:status:{status}"))
            if status_keys:
                base_keys = [k for k in base_keys if k in status_keys]
        
        # Chargement et filtrage des données
        pipe = rdb.pipeline()
        for key in base_keys:
            pipe.hgetall(key)
        
        results = pipe.execute()
        
        # Filtrage supplémentaire
        for i, fixture_data in enumerate(results):
            if not fixture_data:
                continue
                
            # Filtre par ligue
            if league:
                league_match = (
                    league.lower() in fixture_data.get("league", "").lower() or
                    league == fixture_data.get("league_id", "")
                )
                if not league_match:
                    continue
            
            # Filtre par pays
            if country and country.lower() not in fixture_data.get("country", "").lower():
                continue
            
            # Ajoute la clé pour référence
            fixture_data["_key"] = base_keys[i]
            filtered_keys.append(fixture_data)
        
        # Tri par timestamp (plus récent en premier)
        filtered_keys.sort(
            key=lambda x: x.get("timestamp", 0), 
            reverse=True
        )
        
        # Pagination
        total = len(filtered_keys)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_results = filtered_keys[start_idx:end_idx]
        
        duration = time.time() - start_time
        
        return {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size,
            "results": page_results,
            "filters_applied": {
                "status": status,
                "league": league,
                "date": date,
                "country": country
            },
            "query_time": f"{duration:.3f}s"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query error: {str(e)}")

@app.get("/football/filters")
def get_football_filters():
    """
    Retourne dynamiquement les filtres disponibles
    """
    try:
        # Récupère toutes les fixtures des 3 jours
        yesterday, today, tomorrow = get_date_range()
        all_keys = []
        for date in [yesterday, today, tomorrow]:
            all_keys.extend(rdb.keys(f"football:{date}:*"))
        
        if not all_keys:
            return {
                "leagues": [],
                "countries": [],
                "dates": [],
                "statuses": []
            }
        
        # Collecte des filtres en batch
        pipe = rdb.pipeline()
        for key in all_keys:
            pipe.hgetall(key)
        
        results = pipe.execute()
        
        # Extraction des valeurs uniques
        leagues = set()
        countries = set()
        dates = set()
        statuses = set()
        
        for fixture_data in results:
            if fixture_data:
                if fixture_data.get("league"):
                    leagues.add(fixture_data["league"])
                if fixture_data.get("country"):
                    countries.add(fixture_data["country"])
                if fixture_data.get("date"):
                    dates.add(fixture_data["date"])
                if fixture_data.get("status"):
                    statuses.add(fixture_data["status"])
        
        return {
            "leagues": sorted(list(leagues)),
            "countries": sorted(list(countries)),
            "dates": sorted(list(dates), reverse=True),
            "statuses": sorted(list(statuses))
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Filters error: {str(e)}")

@app.get("/debug/last-fetch")
def debug_last_fetch():
    """Debug: analyse la dernière requête de fetch"""
    try:
        # Test simple de l'API football
        yesterday, today, tomorrow = get_date_range()
        headers = {"x-apisports-key": API_KEY}
        url = f"https://v3.football.api-sports.io/fixtures?status=FT&date={yesterday}"
        
        print(f"[DEBUG] Testing API call: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get("response", [])
            
            # Analyse de la première fixture
            sample_fixture = fixtures[0] if fixtures else None
            
            return {
                "api_status": response.status_code,
                "total_fixtures": len(fixtures),
                "sample_fixture_keys": list(sample_fixture.keys()) if sample_fixture else [],
                "sample_fixture_structure": {
                    "fixture_keys": list(sample_fixture.get("fixture", {}).keys()) if sample_fixture else [],
                    "league_keys": list(sample_fixture.get("league", {}).keys()) if sample_fixture else [],
                    "teams_keys": list(sample_fixture.get("teams", {}).keys()) if sample_fixture else [],
                    "goals_keys": list(sample_fixture.get("goals", {}).keys()) if sample_fixture else []
                } if sample_fixture else None,
                "redis_keys_count": len(rdb.keys("football:*")),
                "api_key_used": API_KEY[:10] + "..." if API_KEY else "No API key"
            }
        else:
            return {
                "error": f"API error {response.status_code}",
                "response": response.text[:500]
            }
    except Exception as e:
        return {"error": f"Debug error: {str(e)}"}

@app.get("/debug/test-storage")
def debug_test_storage():
    """Debug: teste le stockage d'une fixture simple"""
    try:
        # Récupère une fixture réelle de l'API
        yesterday, today, tomorrow = get_date_range()
        headers = {"x-apisports-key": API_KEY}
        url = f"https://v3.football.api-sports.io/fixtures?status=FT&date={yesterday}"
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            fixtures = data.get("response", [])
            
            if fixtures:
                test_fixture = fixtures[0]
                
                # Tente de stocker juste cette fixture
                print(f"[DEBUG] Testing storage with fixture: {test_fixture.get('fixture', {}).get('id')}")
                stored = store_fixtures_batch([test_fixture])
                
                # Vérifie si elle a été stockée
                test_key = f"football:{test_fixture['fixture']['date']}:{test_fixture['fixture']['id']}"
                stored_data = rdb.hgetall(test_key)
                
                return {
                    "test_fixture_id": test_fixture['fixture']['id'],
                    "test_fixture_date": test_fixture['fixture']['date'],
                    "storage_result": stored,
                    "redis_key": test_key,
                    "stored_data_exists": bool(stored_data),
                    "stored_data": stored_data if stored_data else None,
                    "fixture_structure": {
                        "fixture": list(test_fixture["fixture"].keys()),
                        "league": list(test_fixture["league"].keys()),
                        "teams": list(test_fixture["teams"].keys()),
                        "goals": list(test_fixture["goals"].keys())
                    }
                }
            else:
                return {"error": "No fixtures returned from API"}
        else:
            return {"error": f"API error {response.status_code}"}
            
    except Exception as e:
        return {"error": f"Test storage error: {str(e)}"}

# ==================== LEGACY ENDPOINTS (pour compatibilité) ====================

@app.get("/results")
def get_all_results():
    """Legacy: retourne tous les résultats (limité à 100)"""
    keys = rdb.keys("football:*")[:100]
    pipe = rdb.pipeline()
    for key in keys:
        pipe.hgetall(key)
    results = pipe.execute()
    return [r for r in results if r]

@app.get("/last-refresh")
def get_last_refresh():
    """Timestamp du dernier refresh"""
    return {"last_refresh": rdb.get("last_refresh")}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
