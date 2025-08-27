import requests
import time
import click

def test_connection():
    url = 'https://atukpostgrest.clubwise.com/'
    try:
        start = time.perf_counter()
        response = requests.head(url, timeout=5)
        end = time.perf_counter()
        response_time = end - start
        if response.status_code < 400:
            print(f"Server is reachable (status code: {response.status_code}) in {response_time:.2f}s")
            return 1
        else:
            print(f"Server responded, but with error status code: {response.status_code} in {response_time:.2f}s")
            return 0
    except requests.exceptions.ConnectionError:
        print("Failed to connect: Server unreachable.")
        return 0
    except requests.exceptions.Timeout:
        print(f"Connection timed out after {timeout} seconds.")
        return 0
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 0