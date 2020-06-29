import json
import pytest

from financial.apps.scraping.models import NemotechModel
from financial.tests.file_fixtures import NEMOS_JSON


pytestmark = pytest.mark.django_db


def read_json(file_path):
    with open(file_path, 'r') as _file:
        raw_json = json.loads(_file.read())

    return raw_json


@pytest.fixture(scope='session')
def insert_nemotech(django_db_blocker):
    with django_db_blocker.unblock():
        nemo_insert = [
            NemotechModel(**_nemo)
            for _nemo in read_json(NEMOS_JSON)
        ]
        NemotechModel.objects.bulk_create(nemo_insert)

        yield
        NemotechModel.objects.all().delete()
