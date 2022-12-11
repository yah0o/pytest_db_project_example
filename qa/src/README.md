# Prodo tests

## How to run tests

0. Creating and activate virtual environment
    ``` 
    $ python3 -m venv srcenv
    $ source srcenv/bin/activate
    ```
   
1. Install tests dependencies to some virtualenv:
    ```
    (virtualenv) $ pip install -r requirements.txt
    ```

2. Create `pytest.ini` config:
    ```
    [pytest]
    addopts = -v --alluredir=.allure/ --yaml-config=env/local.yaml
    ```

3. Run the tests:
    ```
    (virtualenv) $ pytest tests/
    ```

4. (Optional) Generate and open Allure report:
    ```
    $ allure serve .allure/
    ```

## See also

* [Test environment README](../docker/README.md)
* [Allure Test Report](https://confluence.wargaming.net/display/PLATFORM/%5BWTP%5D+Allure+Test+Report)
