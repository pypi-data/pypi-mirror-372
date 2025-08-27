import pytest
from unittest.mock import patch, MagicMock
from kuristo.actions.mpi_action import MPIAction
from kuristo.context import Context


class DummyMPIAction(MPIAction):
    def create_sub_command(self) -> str:
        return "my_mpi_program"


def make_context():
    return MagicMock(spec=Context)


def test_default_num_cores():
    ctx = make_context()
    action = DummyMPIAction(name="mpi_test", context=ctx)
    assert action.num_cores == 1  # default


def test_custom_num_cores():
    ctx = make_context()
    action = DummyMPIAction(name="mpi_test", context=ctx, **{'n-procs': 8})
    assert action.num_cores == 8


@patch("kuristo.actions.mpi_action.config.get")
def test_create_command_uses_config_and_sub_command(mock_get):
    ctx = make_context()
    mock_get.return_value = MagicMock(mpi_launcher="mpirun")
    action = DummyMPIAction(name="mpi_test", context=ctx, **{'n-procs': 4})

    result = action.create_command()

    assert result == "mpirun -np 4 my_mpi_program"
    mock_get.assert_called_once()


def test_cannot_instantiate_abstract_mpi_action():
    ctx = make_context()
    with pytest.raises(TypeError):
        MPIAction(name="mpi_test", context=ctx)  # no sub_command implementation
