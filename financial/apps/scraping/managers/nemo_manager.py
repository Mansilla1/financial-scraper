from django.db.models import Manager
from typing import List

from . import models


class NemotechManager(Manager):

    def bulk_insert(self, nemotech: List[dict]):
        nemo_names = [x.get('nemo') for x in nemotech]
        assert all(x is not None for x in nemo_names)

        nemo_tech_list = self.filter(
            name=nemo_names,
            status=models.NemotechModel.ACTIVE,
        ).values()
        insert_data = []
        update_ids = []

        for _nemo in nemotech:
            _nemo_obj = next(
                filter(
                    lambda x: x['nemo'] == _nemo['nemo'],
                    nemo_tech_list,
                ),
                None,
            )

            if _nemo_obj:
                update_ids.append(_nemo_obj['id'])

            data_to_insert = {
                **_nemo,
                'status': models.NemotechModel.ACTIVE,
            }
            insert_data.append(models.NemotechModel(**data_to_insert))

        self.filter(
            id__in=update_ids,
        ).update(
            status=models.NemotechModel.INACTIVE,
        )

        self.bulk_insert(insert_data)
