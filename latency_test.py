import time
import requests
import json

# --- CONFIGURATION ---
# We use the optimized model we just created
MODEL = "phi3-fast" 
PROMPT = "Write a Python function to calculate the Fibonacci sequence recursively."

def test_latency():
    url = "http://localhost:11434/api/generate"
    headers = {"Content-Type": "application/json"}
    
    # We disable streaming to get the full timing stats in one packet
    data = {
        "model": MODEL,
        "prompt": PROMPT,
        "stream": False 
    }

    print(f"--- 🚀 Testing Model: {MODEL} ---")
    print("Sending request to Gemini API...")
    
    start_wall_time = time.time()
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        end_wall_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            
            # Gemini API returns timing in nanoseconds (ns)
            total_duration_ns = result.get("total_duration", 0)
            load_duration_ns = result.get("load_duration", 0)
            eval_count = result.get("eval_count", 0)       # Number of tokens generated
            eval_duration_ns = result.get("eval_duration", 0) # Time spent generating
            
            # Calculations
            total_time_s = total_duration_ns / 1e9
            load_time_ms = load_duration_ns / 1e6
            # Avoid division by zero
            tokens_per_sec = eval_count / (eval_duration_ns / 1e9) if eval_duration_ns > 0 else 0

            print(f"\n📊 RESULTS:")
            print(f"--------------------------------------------------")
            print(f"Total Time:       {total_time_s:.2f}s")
            print(f"Load Time:        {load_time_ms:.0f}ms (Time to load model into RAM)")
            print(f"Generation Speed: {tokens_per_sec:.2f} tokens/sec")
            print(f"--------------------------------------------------")

            # Benchmarks for Manoj's dev work
            if tokens_per_sec > 30:
                print("✅ VERDICT: Excellent. Real-time capable.")
            elif tokens_per_sec > 10:
                print("✅ VERDICT: Good. Usable for chat assistants.")
            else:
                print("❌ VERDICT: SLOW. Still likely CPU-bound.")
                
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to Gemini API.")
        print("Make sure your GEMINI_API_KEY is set in the .env file")

if __name__ == "__main__":
    test_latency()