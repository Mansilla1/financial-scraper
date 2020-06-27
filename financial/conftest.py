import json
import pytest

from financial.apps.scraping.models import NemotechModel
from financial.tests.file_fixtures import NEMOS_JSON


def read_json(file_path):
    with open(file_path, 'r') as _file:
        raw_json = json.loads(_file.read())

    return raw_json


@pytest.mark.fixture(scope='session')
def insert_nemotech():
    nemo_insert = [
        NemotechModel(**_nemo)
        for _nemo in read_json(NEMOS_JSON)
    ]

    NemotechModel.objects.bulk_create(nemo_insert)

    yield

    NemotechModel.delete()

