# Prodo test environment

## Usage

Test env management is implemented with [Docker Compose](https://docs.docker.com/compose/) and [Invoke](http://docs.pyinvoke.org/) tasks.

0. Creating and activate virtual environment
    ``` 
    $ python3 -m venv dockerenv
    $ source dockerenv/bin/activate
    ```
1. Install tasks dependencies to some virtualenv:
    ```
    (virtualenv) $ pip install -r requirements.txt
    ```
    if you got the issue:
    ``` 
    ld: library not found for -lssl
    clang: error: linker command failed with exit code 1 (use -v to see invocation)
   ```
   try to set ssl library path explicitly
   ```
   (virtualenv) $ LDFLAGS=-L/usr/local/opt/openssl/lib pip install -r requirements.txt
   ```
2. Start all containers and load initial test data:
    ```
   # image with tag master_{last_commit}
   (virtualenv) $ invoke up   
    To check if all service are up you can use wait_services.sh:
    ```
    /qa/docker> ./wait_services.sh
    ```

4. Run tests [README](../src/README.md)

5. In case of env changes - purge all containers, goto 1:
    ```
    (virtualenv) $ invoke down
    # OR
    (virtualenv) $ inv down
    ```

## See also

* [Wiremock dynamic stubbing](http://wiremock.org/docs/response-templating/)
