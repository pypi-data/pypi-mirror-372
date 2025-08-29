#  IBM Confidential
#  PID 5900-BAF
#  Copyright StreamSets Inc., an IBM Company 2024

from streamsets.sdk.sch_models import Roles


class Entity:
    def __init__(self, data) -> None:
        self._data = data


ROLES_LABELS_TO_IDS = {'spiderman': 'role:main', 'uncle ben': 'role:development'}


def test_roles():
    data = {'rolesWeCareAbout': ['role:development'], 'roles': []}

    role_id_to_label = {role_id: role_label for role_label, role_id in ROLES_LABELS_TO_IDS.items()}

    entity = Entity(data)
    roles = Roles(
        values=[role_id_to_label[role_id] for role_id in data['rolesWeCareAbout']],
        entity=entity,
        role_label_to_id=ROLES_LABELS_TO_IDS,
        role_data_key='rolesWeCareAbout',
    )

    roles.append('spiderman')
    # ensure the id got added to the roles we care about
    assert 'role:main' in data['rolesWeCareAbout']
    # default roles is untouched
    assert len(data['roles']) == 0

    assert 'role:development' in data['rolesWeCareAbout']
    roles.remove('uncle ben')
    # ensure the id got removed
    assert 'role:development' not in data['rolesWeCareAbout']
    assert len(data['roles']) == 0
