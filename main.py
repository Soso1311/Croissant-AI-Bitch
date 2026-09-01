from core.listener import wait_for_wake_word, record_until_silence
from core.agent import run_agent
from core.voice import speak


def main():

    print("""
╔════════════════════════════════════╗
║            J A R V I S             ║
║          SYSTEM ONLINE              ║
║          VOICE MODE                 ║
╚════════════════════════════════════╝
""")

    while True:

        try:

            wait_for_wake_word()

            command = record_until_silence()

            if not command:
                print("No command detected.")
                continue

            print(f"⚡ Processing: {command}")

            response = run_agent(
                command,
                status_callback=speak
            )

            print(f"🤖 JARVIS: {response}")

            speak(response)

        except KeyboardInterrupt:

            print("\nJARVIS shutting down.")
            break

        except Exception as e:

            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
