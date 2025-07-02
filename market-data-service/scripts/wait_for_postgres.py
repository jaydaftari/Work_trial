import socket
import time
import sys


def wait_for_postgres(host="db", port=5432, timeout=60):
    start_time = time.time()
    while True:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("Postgres is ready!")
                return True
        except OSError:
            print("Waiting for Postgres...")
            time.sleep(2)
        if time.time() - start_time > timeout:
            print("Timeout waiting for Postgres", file=sys.stderr)
            return False


if __name__ == "__main__":
    success = wait_for_postgres()
    if not success:
        sys.exit(1)
