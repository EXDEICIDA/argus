import sys
from data import System
from interface import TUI


def main():
    print("Initializing Argus...")

    try:
        instance = System()

        app = TUI(instance)

        app.run()

    except KeyboardInterrupt:
        print("\nStopping Monitor...")
        sys.exit(0)


if __name__ == "__main__":
    main()