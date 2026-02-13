# -*- coding: utf-8 -*-
"""
P10 End-to-End Test Script
Tests the complete workflow: create project -> agents work -> game output

Usage:
    python tests/test_p10_end_to_end.py
"""
import asyncio
import sys
import io
import time
import json
from pathlib import Path

# Fix Windows encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import httpx

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws/test_p10_client"

# Test results collector
test_results = []


def record(name, passed, detail=""):
    """Record test result"""
    status = "PASS" if passed else "FAIL"
    test_results.append({"name": name, "passed": passed, "detail": detail})
    print(f"  [{status}] {name}" + (f" - {detail}" if detail else ""))


async def test_1_health_check():
    """Test 1: Health check endpoint"""
    print("\n--- Test 1: Health Check ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/api/health", timeout=10)
            data = resp.json()
            record("Health endpoint returns 200", resp.status_code == 200)
            record("Status is healthy", data.get("status") == "healthy")
            record("Service name correct", data.get("service") == "AI Game Studio")
    except Exception as e:
        record("Health check", False, str(e))


async def test_2_project_list():
    """Test 2: Project list (should be empty or have previous projects)"""
    print("\n--- Test 2: Project List ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/api/projects", timeout=10)
            data = resp.json()
            record("Projects endpoint returns 200", resp.status_code == 200)
            record("Has total field", "total" in data)
            record("Has projects array", isinstance(data.get("projects"), list))
    except Exception as e:
        record("Project list", False, str(e))


async def test_3_websocket_connection():
    """Test 3: WebSocket connection"""
    print("\n--- Test 3: WebSocket Connection ---")
    try:
        import websockets
        
        async with websockets.connect(WS_URL, close_timeout=5) as ws:
            # Should receive connected event
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            data = json.loads(msg)
            record("WS connected event received", data.get("event") == "connected")
            record("WS client_id correct", data.get("client_id") == "test_p10_client")
            
            # Test ping/pong
            await ws.send(json.dumps({"type": "ping"}))
            pong = await asyncio.wait_for(ws.recv(), timeout=5)
            pong_data = json.loads(pong)
            record("WS ping/pong works", pong_data.get("event") == "pong")
            
    except ImportError:
        record("WebSocket test (websockets not installed)", False, "pip install websockets")
    except Exception as e:
        record("WebSocket connection", False, str(e))


async def test_4_create_project():
    """Test 4: Create a project and start the workflow"""
    print("\n--- Test 4: Create Project ---")
    project_id = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{BASE_URL}/api/project/start",
                json={
                    "game_idea": "A simple click counter game. Click a button to increase the number. Show the count on screen.",
                    "project_name": "p10_counter_test"
                },
                timeout=30
            )
            data = resp.json()
            record("Create project returns 200", resp.status_code == 200)
            record("Project creation success", data.get("success") == True)
            
            project_id = data.get("project_id")
            record("Project ID returned", project_id is not None, project_id or "")
            
    except Exception as e:
        record("Create project", False, str(e))
    
    return project_id


async def test_5_monitor_workflow(project_id: str):
    """Test 5: Monitor workflow progress"""
    print("\n--- Test 5: Monitor Workflow Progress ---")
    if not project_id:
        record("Monitor workflow (no project ID)", False, "Skipped")
        return
    
    max_wait = 600  # 10 minutes max
    poll_interval = 10  # poll every 10 seconds
    elapsed = 0
    last_phase = ""
    phases_seen = set()
    final_status = None
    
    try:
        while elapsed < max_wait:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval
            
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{BASE_URL}/api/project/{project_id}/status",
                    timeout=10
                )
                
                if resp.status_code != 200:
                    print(f"  [{elapsed}s] Status check failed: {resp.status_code}")
                    continue
                
                status = resp.json()
                current_phase = status.get("current_phase", "unknown")
                progress = status.get("progress", 0)
                project_status = status.get("status", "unknown")
                
                if current_phase != last_phase:
                    print(f"  [{elapsed}s] Phase: {current_phase} | Progress: {progress}% | Status: {project_status}")
                    last_phase = current_phase
                    phases_seen.add(current_phase)
                
                if project_status in ("completed", "failed"):
                    final_status = project_status
                    print(f"  [{elapsed}s] Workflow {project_status}!")
                    break
        
        record("Workflow completed within timeout", final_status is not None, f"{elapsed}s elapsed")
        record("Workflow status is completed", final_status == "completed", f"actual: {final_status}")
        record("Multiple phases observed", len(phases_seen) > 1, f"phases: {phases_seen}")
        
    except Exception as e:
        record("Monitor workflow", False, str(e))
    
    return final_status


async def test_6_verify_output(project_id: str):
    """Test 6: Verify game output files"""
    print("\n--- Test 6: Verify Output Files ---")
    if not project_id:
        record("Verify output (no project ID)", False, "Skipped")
        return
    
    # The workflow uses project_name (not project_id) as the folder name
    # project_id = "p10_counter_test_YYYYMMDD_HHMMSS"
    # project_name = "p10_counter_test"
    project_name = "p10_counter_test"
    project_dir = Path(__file__).parent.parent / "projects" / project_name
    output_dir = project_dir / "output"
    knowledge_dir = project_dir / "shared_knowledge"
    
    # Check project directory exists
    record("Project directory exists", project_dir.exists(), str(project_dir))
    
    # Check shared knowledge files
    knowledge_files = [
        "project_rules.yaml",
        "game_design_doc.md",
        "tech_design_doc.md",
        "api_registry.yaml",
        "config_tables.yaml",
        "art_asset_list.yaml",
        "bug_tracker.yaml",
        "decision_log.yaml"
    ]
    
    for f in knowledge_files:
        file_path = knowledge_dir / f
        exists = file_path.exists()
        size = file_path.stat().st_size if exists else 0
        record(f"Knowledge file: {f}", exists and size > 0, f"{size} bytes")
    
    # Check output files
    html_path = output_dir / "index.html"
    js_path = output_dir / "game.js"
    
    record("Output index.html exists", html_path.exists())
    record("Output game.js exists", js_path.exists())
    
    if html_path.exists():
        html_content = html_path.read_text(encoding='utf-8')
        record("HTML has <html> tag", "<html" in html_content.lower())
        record("HTML has <canvas> or <body>", "<canvas" in html_content.lower() or "<body" in html_content.lower())
        record("HTML file size > 100 bytes", len(html_content) > 100, f"{len(html_content)} bytes")
    
    if js_path.exists():
        js_content = js_path.read_text(encoding='utf-8')
        record("JS file size > 100 bytes", len(js_content) > 100, f"{len(js_content)} bytes")
    
    # Check for art assets
    assets_dir = output_dir / "assets"
    if assets_dir.exists():
        png_files = list(assets_dir.glob("*.png"))
        record("Art assets generated", len(png_files) > 0, f"{len(png_files)} PNG files")
    else:
        record("Art assets directory exists", False, "assets/ not found")


async def test_7_frontend_accessible():
    """Test 7: Frontend page accessible"""
    print("\n--- Test 7: Frontend Accessible ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/", timeout=10)
            record("Frontend returns 200", resp.status_code == 200)
            record("HTML content returned", "html" in resp.text.lower())
            record("Has office-canvas element", "office-canvas" in resp.text or "office" in resp.text.lower())
    except Exception as e:
        record("Frontend accessible", False, str(e))


async def test_8_api_docs():
    """Test 8: API docs accessible"""
    print("\n--- Test 8: API Docs ---")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/api/docs", timeout=10)
            record("API docs accessible", resp.status_code == 200)
    except Exception as e:
        record("API docs", False, str(e))


async def main():
    print("=" * 70)
    print("P10 End-to-End Test Suite")
    print("=" * 70)
    print(f"Target: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    start_time = time.time()
    
    # Phase 1: Basic connectivity tests
    await test_1_health_check()
    await test_2_project_list()
    await test_3_websocket_connection()
    await test_7_frontend_accessible()
    await test_8_api_docs()
    
    # Phase 2: Full workflow test
    project_id = await test_4_create_project()
    
    if project_id:
        final_status = await test_5_monitor_workflow(project_id)
        await test_6_verify_output(project_id)
    
    # Summary
    elapsed = time.time() - start_time
    passed = sum(1 for r in test_results if r["passed"])
    total = len(test_results)
    failed = total - passed
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    
    for r in test_results:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{status}] {r['name']}" + (f" ({r['detail']})" if r['detail'] else ""))
    
    print("=" * 70)
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")
    print(f"Pass rate: {passed/total*100:.1f}%")
    print(f"Elapsed: {elapsed:.1f}s")
    print("=" * 70)
    
    # Write results to file for later analysis
    results_file = Path(__file__).parent / "p10_test_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "total": total,
            "passed": passed,
            "failed": failed,
            "elapsed_seconds": elapsed,
            "results": test_results
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nResults saved to: {results_file}")
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
