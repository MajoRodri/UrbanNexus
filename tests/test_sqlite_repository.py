import pytest
from unittest.mock import MagicMock
from repositories.sqlite_repository import SQLiteRepository, RecordNotFoundError


@pytest.fixture
def repo():
    mock_db = MagicMock()
    return SQLiteRepository(mock_db)


def test_create_zone(repo):
    repo.db.add = MagicMock()
    repo.db.commit = MagicMock()
    repo.db.refresh = MagicMock()

    result = repo.create_zone("Madrid", "1234", 1, "Estacion A")

    assert repo.db.add.called
    assert repo.db.commit.called


def test_get_zone_by_id(repo):
    fake_obj = MagicMock()
    repo.db.query().filter().first.return_value = fake_obj

    result = repo.get_zone_by_id(1)

    assert result == fake_obj


def test_record_not_found(repo):
    repo.db.query().filter().first.return_value = None

    with pytest.raises(RecordNotFoundError):
        repo.get_zone_by_id(999)


def test_delete_zone(repo):
    fake_obj = MagicMock()
    repo.db.query().filter().first.return_value = fake_obj

    repo.db.delete = MagicMock()
    repo.db.commit = MagicMock()

    result = repo.delete_zone(1)

    assert repo.db.delete.called
    
    