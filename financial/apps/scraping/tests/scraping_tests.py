import json
import pytest

from financial.apps.scraping.models import NemotechModel
from .input_files import NEMOS_JSON


pytestmark = pytest.mark.django_db


class TestScraping:

    @pytest.mark.usefixtures('insert_nemotech')
    @pytest.mark.parametrize('input_data', [
        [
            {
                'green_bonus': 0,
                'djsi': 0,
                'isin': 'US0378331005',
                'coin': 'USD',
                'amount': 0,
                'nemo': 'TECH-K',
                'weight': 0,
                'close_price': 357.16,
                'buy_price': 0,
                'sell_price': 0,
                'traded_units': 0,
                'variant': 0,
            },
        ],
        json.loads(open(NEMOS_JSON).read()),
    ])
    def test_bulk_insert(self, input_data):
        nemo_names = list(map(lambda x: x['nemo'], input_data))
        NemotechModel.objects.bulk_insert(input_data)

        assert NemotechModel.objects.filter(
            nemo__in=nemo_names,
        ).exists()
