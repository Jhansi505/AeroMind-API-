from llm.gemini_client import query_llm
from llm.ollama_client import query_ollama
from utils import get_logger
from utils.drone_visualizer import get_visualizer
from tools import *
from config.agent_config import SYSTEM_PROMPT
import json

logger = get_logger("AgenticDrone")


def run_drone_agent():
    print("\n=== Agentic Drone System (Gemini primary, Ollama fallback) ===")
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

        # If user invoked a direct tool command like 'takeoff 100' or movement commands,
        # run locally and skip LLM.
        import re

        # Speed control: 'speed 4' to make animation 4x faster
        speed_cmd = re.search(r"\bspeed\b\s*(\d+(?:\.\d+)?)", user_input, re.IGNORECASE)
        if speed_cmd:
            factor = float(speed_cmd.group(1))
            try:
                viz = get_visualizer()
                viz.set_animation_speed(factor)
                print(f"Animation speed set to {factor}x")
            except Exception as e:
                print(f"Failed to set animation speed: {e}")

            print("-" * 60)
            continue

        # TAKEOFF: e.g., 'takeoff 100' or 'takeoff 100 meters'
        direct_cmd = re.search(r"\b(takeoff)\b\s*(\d+(?:\.\d+)?)", user_input, re.IGNORECASE)
        if direct_cmd:
            cmd = direct_cmd.group(1).lower()
            value = float(direct_cmd.group(2))
            logger.info(f"Direct command detected: {cmd} {value}")
            fn = globals().get(cmd)
            if fn:
                try:
                    result = fn(value)
                    print(result)
                except Exception as e:
                    print(f"Error executing {cmd}: {e}")
            else:
                print(f"Unknown direct command: {cmd}")

            print("-" * 60)
            continue

        # MOVEMENT: 'move forward 10', 'move backward 5 meters', 'move up 3', etc.
        mv = re.search(r"\bmove\b\s*(forward|backward|right|left|up|down)\b\s*(\-?\d+(?:\.\d+)?)", user_input, re.IGNORECASE)
        if mv:
            direction = mv.group(1).lower()
            distance = float(mv.group(2))
            map_fn = {
                'forward': 'move_forward',
                'backward': 'move_backward',
                'right': 'move_right',
                'left': 'move_left',
                'up': 'move_up',
                'down': 'move_down',
            }
            fn_name = map_fn.get(direction)
            fn = globals().get(fn_name)
            logger.info(f"Direct movement detected: {fn_name}({distance})")
            if fn:
                try:
                    result = fn(distance)
                    print(result)
                except Exception as e:
                    print(f"Error executing movement {direction}: {e}")
            else:
                print(f"Movement function {fn_name} not found.")

            print("-" * 60)
            continue

        # MOVE TO XYZ: 'move to 10 20 30' or 'move to 10,20,30'
        mv_to = re.search(r"\bmove\s+to\b\s*\(?\s*(\-?\d+(?:\.\d+)?)[,\s]+(\-?\d+(?:\.\d+)?)[,\s]+(\-?\d+(?:\.\d+)?)", user_input, re.IGNORECASE)
        if mv_to:
            x = float(mv_to.group(1))
            y = float(mv_to.group(2))
            z = float(mv_to.group(3))
            logger.info(f"Direct move_to_location detected: {x}, {y}, {z}")
            fn = globals().get('move_to_location')
            if fn:
                try:
                    result = fn(x, y, z)
                    print(result)
                except Exception as e:
                    print(f"Error executing move_to_location: {e}")
            else:
                print("move_to_location function not available.")

            print("-" * 60)
            continue

        # LAND or RETURN: simple keywords
        if re.search(r"\bland\b", user_input, re.IGNORECASE):
            fn = globals().get('land')
            if fn:
                try:
                    print(fn())
                except Exception as e:
                    print(f"Error landing: {e}")
            else:
                print("land function not available.")
            print("-" * 60)
            continue

        if re.search(r"\breturn to base\b|\breturn home\b|\breturn to home\b", user_input, re.IGNORECASE):
            # Prefer mission-level landing helper when available
            fn = globals().get('return_to_base_and_land') or globals().get('return_to_home')
            if fn:
                try:
                    print(fn())
                except Exception as e:
                    print(f"Error returning home: {e}")
            else:
                print("return function not available.")
            print("-" * 60)
            continue

        prompt = f"{SYSTEM_PROMPT}\nUser: {user_input}\nAgent:"

        # First try Gemini
        try:
            response = query_llm(prompt)
        except RuntimeError as e:
            msg = str(e)
            logger.warning(f"Gemini error: {msg}")
            # Detect quota / resource exhausted
            if "RESOURCE_EXHAUSTED" in msg or "quota" in msg.lower() or "exceeded" in msg.lower():
                print("[WARN] Gemini quota exhausted or rate-limited — attempting Ollama fallback.")
                try:
                    response = query_ollama(prompt)
                except Exception as oe:
                    logger.error(f"Ollama fallback failed: {oe}")
                    print("Both Gemini and Ollama failed. See logs for details.")
                    continue
            else:
                # Other Gemini error: surface and continue loop
                logger.error(f"Gemini unexpected error: {msg}")
                print(f"Error from Gemini: {msg}")
                continue

        # The LLM response may include streaming/extra human text plus a JSON tool call.
        # Try to extract a JSON object that contains the 'tool' key.
        def extract_tool_json(text: str):
            idx = text.find('{"tool"')
            if idx == -1:
                idx = text.find('"tool"')
                if idx == -1:
                    return None, text
                # backtrack to opening brace
                brace_idx = text.rfind('{', 0, idx)
                if brace_idx == -1:
                    return None, text
                start = brace_idx
            else:
                start = text.find('{', idx)

            # Find matching closing brace using a stack
            stack = 0
            end = None
            for i in range(start, len(text)):
                if text[i] == '{':
                    stack += 1
                elif text[i] == '}':
                    stack -= 1
                    if stack == 0:
                        end = i + 1
                        break

            if end is None:
                return None, text

            candidate = text[start:end]
            try:
                obj = json.loads(candidate)
                return obj, text[:start] + text[end:]
            except Exception:
                return None, text

        tool_call, remaining = extract_tool_json(response)
        if tool_call and isinstance(tool_call, dict) and "tool" in tool_call:
            tool_name = tool_call["tool"]
            args = tool_call.get("args", {})

            logger.info(f"Executing tool: {tool_name}")

            tool_fn = globals().get(tool_name)
            if tool_fn:
                try:
                    result = tool_fn(**args)
                    print(f"[TOOL OUTPUT] {result}")
                except Exception as e:
                    print(f"Error running tool {tool_name}: {e}")
            else:
                print("Unknown tool requested.")

            # Print any remaining non-JSON text as agent response
            if remaining and remaining.strip():
                print("\n[AGENT RESPONSE]")
                print(remaining)
        else:
            print("\n[AGENT RESPONSE]")
            print(response)

        print("-" * 60)


if __name__ == "__main__":
    run_drone_agent()
