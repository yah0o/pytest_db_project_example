import io
import json
import os
import re
import sys
import tarfile

import requests
from capi_lib_python.contracts import Contract, ContractsContainer


def load_capi_from_artifactory_and_path(stable_capi_url, unstable_capi_url, draft_capi_path):
    pattern = re.compile(".*[.]json")

    # Load from artifactory
    container = ContractsContainer()
    for url in [stable_capi_url, unstable_capi_url]:
        try:
            response = requests.get(url, stream=True)
            file_obj = io.BytesIO(response.content)
            with tarfile.open(fileobj=file_obj, mode='r:gz') as tar:
                for member in tar.getmembers():
                    if pattern.match(member.name):
                        with tar.extractfile(member) as contract_file:
                            content = contract_file.read()
                            container.add(Contract(json.loads(content)))
        except:
            print("Error on getting contracts from artifactory.", sys.exc_info()[0])

    # Load draft contracts
    with os.scandir(draft_capi_path) as files:
        for file in files:
            if pattern.match(file.name):
                with open(file, 'r') as contract_file:
                    content = contract_file.read()
                    container.add(Contract(json.loads(content)))

    return container
