import argparse
import subprocess
import os

def start_bot() -> None:
    subprocess.run(["poetry", "run", "python", "scripts/start_bot.py"])

def run_tests() -> None:
    os.environ["TESTING"] = "True"  # Устанавливаем перед импортами
    subprocess.run(args=["poetry", "run", "pytest", "app/tests"], env=os.environ)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["start", "test"])
    args = parser.parse_args()

    if args.command == "start":
        start_bot()
    elif args.command == "test":
        run_tests()

if __name__ == "__main__":
    main()