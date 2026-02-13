# -*- coding: utf-8 -*-
"""
P10 Step-by-step Test
Outputs results to a file to avoid Windows encoding issues
"""
import asyncio
import sys
import time
import json
from pathlib import Path

import httpx

BASE_URL = "http://localhost:8000"
LOG_FILE = Path(__file__).parent / "p10_test_log.txt"

def log(msg):
    """Write to log file and stdout"""
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(msg + "\n")
    try:
        print(msg)
    except:
        pass


async def run_step(step_name):
    """Run a specific test step"""
    
    if step_name == "health":
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{BASE_URL}/api/health", timeout=10)
            log(f"Health check: {resp.status_code} {resp.text}")
            return resp.status_code == 200
    
    elif step_name == "create":
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{BASE_URL}/api/project/start",
                json={
                    "game_idea": "A simple click counter game. Click a button and the number increases by 1. Display the count in the center of the screen.",
                    "project_name": "p10_counter"
                },
                timeout=30
            )
            data = resp.json()
            log(f"Create project: {resp.status_code}")
            log(f"Response: {json.dumps(data, ensure_ascii=False, indent=2)}")
            return data.get("project_id")
    
    elif step_name == "status":
        # Read project ID from previous step
        results_path = Path(__file__).parent / "p10_project_id.txt"
        if not results_path.exists():
            log("ERROR: No project ID file found")
            return False
        project_id = results_path.read_text().strip()
        
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{BASE_URL}/api/project/{project_id}/status",
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                log(f"Status: phase={data.get('current_phase')} progress={data.get('progress')} status={data.get('status')}")
                return data
            else:
                log(f"Status check failed: {resp.status_code} {resp.text}")
                return None
    
    elif step_name == "monitor":
        # Read project ID
        results_path = Path(__file__).parent / "p10_project_id.txt"
        if not results_path.exists():
            log("ERROR: No project ID file found")
            return False
        project_id = results_path.read_text().strip()
        
        max_wait = 600
        elapsed = 0
        interval = 10
        last_phase = ""
        
        while elapsed < max_wait:
            await asyncio.sleep(interval)
            elapsed += interval
            
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{BASE_URL}/api/project/{project_id}/status",
                    timeout=10
                )
                if resp.status_code != 200:
                    log(f"  [{elapsed}s] Status check failed: {resp.status_code}")
                    continue
                
                data = resp.json()
                phase = data.get("current_phase", "?")
                status = data.get("status", "?")
                progress = data.get("progress", 0)
                
                if phase != last_phase:
                    log(f"  [{elapsed}s] Phase: {phase} | Progress: {progress} | Status: {status}")
                    last_phase = phase
                
                if status in ("completed", "failed"):
                    log(f"  FINAL: {status} at {elapsed}s")
                    return status
        
        log(f"  TIMEOUT after {max_wait}s")
        return "timeout"
    
    elif step_name == "verify":
        project_name = "p10_counter"
        project_dir = Path(__file__).parent.parent / "projects" / project_name
        output_dir = project_dir / "output"
        knowledge_dir = project_dir / "shared_knowledge"
        
        log(f"\nVerifying output for project: {project_name}")
        log(f"Project dir: {project_dir}")
        log(f"Project dir exists: {project_dir.exists()}")
        
        if knowledge_dir.exists():
            for f in knowledge_dir.iterdir():
                log(f"  Knowledge: {f.name} ({f.stat().st_size} bytes)")
        
        if output_dir.exists():
            for f in output_dir.rglob("*"):
                if f.is_file():
                    log(f"  Output: {f.relative_to(output_dir)} ({f.stat().st_size} bytes)")
        
        html_path = output_dir / "index.html"
        js_path = output_dir / "game.js"
        
        log(f"\nindex.html exists: {html_path.exists()}")
        log(f"game.js exists: {js_path.exists()}")
        
        if html_path.exists():
            content = html_path.read_text(encoding='utf-8')
            log(f"HTML size: {len(content)} chars")
            log(f"HTML has <html>: {'<html' in content.lower()}")
        
        if js_path.exists():
            content = js_path.read_text(encoding='utf-8')
            log(f"JS size: {len(content)} chars")
        
        return True


async def main():
    step = sys.argv[1] if len(sys.argv) > 1 else "health"
    
    # Clear log file for fresh run
    if step == "health":
        LOG_FILE.write_text(f"P10 Test Log - {time.strftime('%Y-%m-%d %H:%M:%S')}\n{'='*60}\n", encoding='utf-8')
    
    log(f"\n--- Step: {step} ---")
    
    result = await run_step(step)
    
    if step == "create" and result:
        # Save project ID for later steps
        pid_file = Path(__file__).parent / "p10_project_id.txt"
        pid_file.write_text(str(result), encoding='utf-8')
        log(f"Project ID saved: {result}")
    
    log(f"Step {step} result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
