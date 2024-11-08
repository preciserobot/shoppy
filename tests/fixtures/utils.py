import docker
import pytest
import time
from redis import Redis, ConnectionError
from app.config import REDIS_PORT
import threading
import http.server

# HTTP Server

class HTTPServer:
    def __init__(self, directory, handler=http.server.SimpleHTTPRequestHandler):
        # Create a new socket and bind to a random port
        self.directory = directory
        self.host = 'localhost'
        self.server = http.server.HTTPServer(
            (self.host, 0),
            lambda *args, **kwargs: handler(*args, directory=self.directory, **kwargs))
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True  # Allow the thread to be killed when tests end

    def url(self):
        # return the servers address
        return f"http://{self.host}:{self.port}"

    # Context manager methods
    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()


# REDIS FIXTURE

@pytest.fixture(scope='session', autouse=True)
def redis():
    container_name = "pytest_redis"
    client = docker.from_env()
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound:
        container = client.containers.run("redis", name=container_name, detach=True, auto_remove=True, ports={f'6379/tcp': ("0.0.0.0", REDIS_PORT)})
    except docker.errors.APIError as e:
        print(f"An error occurred: {e}")
    
    # wait until redis is ready
    while True:
        try:
            Redis(host='localhost', port=REDIS_PORT).ping()
            break
        except ConnectionError:
            time.sleep(0.1)
        except Exception as e:
            print(f"An error occurred: {e}")
            break

    yield

    container.stop()

# TIMING STUFF

@pytest.fixture(scope="function", autouse=True)
def time_test():
    """ Time a test and print out how long it took """
    before = time.time()
    yield
    after = time.time()
    print(f"\nTest took {after - before:.02f} seconds!")


@pytest.fixture(scope="session", autouse=True)
def time_all_tests():
    """ Time a test and print out how long it took """
    before = time.time()
    yield
    after = time.time()
    print(f"\nTotal test time: {after - before:.02f} seconds!")