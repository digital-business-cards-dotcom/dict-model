import shutil

import pytest

from . import TEST_FILES


@pytest.fixture(autouse=True)
def reset_lookup(mocker):
    mocker.patch.dict("dict_model.serializers.DICT_MODEL_CLASSES", {})
    mocker.patch.dict("dict_model.lookup.DICT_MODEL_CLASSES", {})


@pytest.fixture(autouse=True)
def clean_files():
    if TEST_FILES.exists():
        shutil.rmtree(TEST_FILES)

    TEST_FILES.mkdir(parents=True, exist_ok=True)
    yield

    if TEST_FILES.exists():
        shutil.rmtree(TEST_FILES)
