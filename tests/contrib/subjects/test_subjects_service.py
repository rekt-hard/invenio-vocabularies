# -*- coding: utf-8 -*-
#
# Copyright (C) 2021 CERN.
# Copyright (C) 2021 Northwestern University.
#
# Invenio-Vocabularies is free software; you can redistribute it and/or
# modify it under the terms of the MIT License; see LICENSE file for more
# details.

"""Test the subject vocabulary service."""

import pytest
from invenio_pidstore.errors import PIDDeletedError

from invenio_vocabularies.contrib.subjects.api import Subject


def test_subject_simple_flow(app, db, service, identity, subject_full_data):
    """Test a simple vocabulary service flow."""
    # Create a controlled subject
    item = service.create(identity, subject_full_data)
    id_ = item.id
    data = item.data

    assert id_ == subject_full_data['id']
    for k, v in subject_full_data.items():
        assert data[k] == v, data

    # Read it
    read_item = service.read(identity, 'https://id.nlm.nih.gov/mesh/D000001')
    assert item.id == read_item.id
    assert item.data == read_item.data

    # Refresh index to make changes live.
    Subject.index.refresh()

    # Search it
    # Because colons are special characters in a query, we must place
    # quotes around id_ which contains colons
    res = service.search(identity, q=f'id:"{id_}"', size=25, page=1)
    assert res.total == 1
    assert list(res.hits)[0] == read_item.data

    # Update it
    data = read_item.data
    data['subject'] = 'Antibiotics'
    update_item = service.update(identity, id_, data)
    assert item.id == update_item.id
    assert update_item['subject'] == 'Antibiotics'

    # Delete it
    assert service.delete(identity, id_)

    # Refresh to make changes live
    Subject.index.refresh()

    # Fail to retrieve it
    # - db
    pytest.raises(PIDDeletedError, service.read, identity, id_)
    # - search
    res = service.search(identity, q=f'id:"{id_}"', size=25, page=1)
    assert res.total == 0
