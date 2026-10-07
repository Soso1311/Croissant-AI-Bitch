import argparse
import sys
from core.agent import AutonomousAgent

def main():
    parser = argparse.ArgumentParser(description="Croissant-AI-Bitch: Secure Autonomous Agent")
    parser.add_argument("--goal", type=str, help="Run a specific autonomous goal directly.")
    args = parser.parse_args()

    agent = AutonomousAgent()

    print("==================================================")
    print("🤖 CROISSANT JARVIS AUTONOMOUS AGENT ONLINE")
    print("Security: Sandboxed Workspace + Interceptor Enabled")
    print("==================================================")

    if args.goal:
        result = agent.run(args.goal)
        print(f"\n✅ Result:\n{result}")
        return

    while True:
        try:
            user_input = input("\nJarvis > ").strip()
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Shutting down Jarvis.")
                break
            if not user_input:
                continue

            result = agent.run(user_input)
            print(f"\n✅ Result:\n{result}")

        except KeyboardInterrupt:
            print("\nSession interrupted.")
            sys.exit(0)

if __name__ == "__main__":
    main()
