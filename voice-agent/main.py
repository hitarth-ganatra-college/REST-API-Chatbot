from session_handler import run
import websockets

print("WEBSOCKETS LIB PATH:", websockets.__file__)
print("WEBSOCKETS VERSION:", websockets.__version__)

if __name__ == "__main__":
    print("Voice agent starting...")
    run()