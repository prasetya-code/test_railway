from flask import Flask
from unittest.mock import patch

from app.routes import register_routes


class DummyBlueprint:
    pass


# ==========================================================
# SUCCESS PATH
# ==========================================================

def test_register_routes_success():
    """
    Cover:
    - import main_bp
    - import monitor_bp
    - register blueprint 1
    - register blueprint 2
    """

    app = Flask(__name__)

    registered = []

    def fake_register(bp):
        registered.append(bp)

    with patch.object(
        app,
        "register_blueprint",
        side_effect=fake_register
    ):
        register_routes(app)

    assert len(registered) == 2


# ==========================================================
# EXCEPTION PATH
# ==========================================================

@patch("app.routes.traceback.print_exc")
def test_register_routes_exception(mock_print_exc):
    """
    Cover:
    - except block
    - traceback.print_exc()
    """

    app = Flask(__name__)

    with patch.object(
        app,
        "register_blueprint",
        side_effect=Exception("register failed")
    ):
        register_routes(app)

    mock_print_exc.assert_called_once()


# ==========================================================
# ERROR MESSAGE PATH
# ==========================================================

@patch("app.routes.traceback.print_exc")
def test_register_routes_print_message(mock_print_exc):
    """
    Cover:
    - print message
    - print error
    """

    app = Flask(__name__)

    with patch("builtins.print") as mock_print:
        with patch.object(
            app,
            "register_blueprint",
            side_effect=Exception("boom")
        ):
            register_routes(app)

    assert mock_print.call_count == 2

    first_call = mock_print.call_args_list[0]
    second_call = mock_print.call_args_list[1]

    assert (
        "ROUTE gagal di regis dan inisialisasi di create_app()"
        in first_call.args[0]
    )

    assert second_call.args[0] == "ERROR:"
    assert str(second_call.args[1]) == "boom"


# ==========================================================
# VERIFY IMPORTS WORK
# ==========================================================

def test_blueprints_can_be_imported():
    """
    Memastikan line import dalam register_routes
    memang valid dan executable.
    """

    from app.routes.app_routes import main_bp
    from app.routes.monitor_routes import monitor_bp

    assert main_bp is not None
    assert monitor_bp is not None


# ==========================================================
# VERIFY TWO BLUEPRINTS REGISTERED
# ==========================================================

def test_register_routes_registers_exactly_two_blueprints():

    app = Flask(__name__)

    count = 0

    def fake_register(_):
        nonlocal count
        count += 1

    with patch.object(
        app,
        "register_blueprint",
        side_effect=fake_register
    ):
        register_routes(app)

    assert count == 2