import httpx

BASE_URL = "http://127.0.0.1:8000"

def test_endpoints():
    client = httpx.Client(base_url=BASE_URL, timeout=60.0)

    print("--- 1. GET /api/health ---")
    r = client.get("/api/health")
    print(r.status_code, r.text)

    print("\n--- 2. GET /api/repositories ---")
    r = client.get("/api/repositories")
    print(r.status_code, r.text[:200])

    repo_id = "flask"
    print(f"\n--- 3. GET /api/repositories/{repo_id} ---")
    r = client.get(f"/api/repositories/{repo_id}")
    print(r.status_code, r.text[:200])

    print(f"\n--- 4. GET /api/repositories/{repo_id}/structure ---")
    r = client.get(f"/api/repositories/{repo_id}/structure")
    print(r.status_code, r.text[:200])

    print(f"\n--- 5. GET /api/repositories/{repo_id}/file ---")
    r = client.get(f"/api/repositories/{repo_id}/file?path=src/flask/app.py")
    print(r.status_code, r.text[:200])

    print(f"\n--- 6. POST /api/repositories/{repo_id}/search ---")
    r = client.post(f"/api/repositories/{repo_id}/search", json={"query": "Flask"})
    print(r.status_code, r.text[:200])

    print(f"\n--- 7. GET /api/repositories/{repo_id}/symbols/Flask ---")
    r = client.get(f"/api/repositories/{repo_id}/symbols/Flask")
    print(r.status_code, r.text[:200])

    print(f"\n--- 8. GET /api/repositories/{repo_id}/relationships/Flask ---")
    r = client.get(f"/api/repositories/{repo_id}/relationships/Flask")
    print(r.status_code, r.text[:200])

    print(f"\n--- 9. POST /api/repositories/{repo_id}/ask ---")
    r = client.post(f"/api/repositories/{repo_id}/ask", json={"question": "What is Flask?"})
    print(r.status_code, r.text[:200])

if __name__ == "__main__":
    test_endpoints()
