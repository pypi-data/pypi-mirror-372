"""Tests for project's installation feature."""


import pytest
from typing import Generator

from commitizen.out import success


class TestMigrate:

    @pytest.fixture(scope="session")
    def setup_teardown(self) -> Generator[bool, None, None]:
        something: bool = False
        yield something

    class TestFrom__0_20_2:

        def test_should_return_true_if_install_is_successful(self) -> None:
            pass
