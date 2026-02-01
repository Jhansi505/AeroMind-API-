from llm.gemini_client import query_llm
from utils import get_logger
from utils.drone_visualizer import get_visualizer
from tools import *
from config.agent_config import SYSTEM_PROMPT
import json

logger = get_logger("AgenticDrone")


def run_drone_agent():
    print("\n=== Agentic Drone System (Gemini AI + OpenCV) ===")
    print("Type 'exit' or 'quit' to stop\n")
    
    # Start 3D visualization
    visualizer = get_visualizer()
    visualizer.start_visualization()
    print("[INFO] 3D visualization started\n")

    while True:
        user_input = input("Mission Command > ").strip()

        if user_input.lower() in {"exit", "quit"}:
            print("Shutting down agent...")
            visualizer.stop_visualization()
            break

        prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}\nAgent:"
        response = query_llm(prompt)

        try:
            tool_call = json.loads(response)

            if "tool" in tool_call:
                tool_name = tool_call["tool"]
                args = tool_call.get("args", {})

                logger.info(f"Executing tool: {tool_name}")

                tool_fn = globals().get(tool_name)
                if tool_fn:
                    result = tool_fn(**args)
                    print(f"[TOOL OUTPUT] {result}")
                else:
                    print("Unknown tool requested.")

        except json.JSONDecodeError:
            print("\n[AGENT RESPONSE]")
            print(response)

        print("-" * 60)


if __name__ == "__main__":
    run_drone_agent()