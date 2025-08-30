# Tests for the decoder's get_traits() function.
from typing import Dict

import pytest

pytestmark = pytest.mark.unit

from decoder import decoder


def test_check_all_traits():
    # Arrange

    # Act

    # Assert
    assert len(decoder.ALL_TRAITS) == 1
    assert decoder.TRAIT_COMBINE in decoder.ALL_TRAITS


def test_get_traits_when_none():
    # Arrange
    job_definition: Dict = {}

    # Act
    traits = decoder.get_traits(job_definition)

    # Assert
    assert traits == []


def test_get_traits_when_combine():
    # Arrange
    job_definition: Dict = {"traits": [{"combine": "source"}]}

    # Act
    traits = decoder.get_traits(job_definition)

    # Assert
    assert len(traits) == 1
    assert traits[0] == {"combine": "source"}
