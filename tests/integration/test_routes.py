from flask import Flask
from unittest.mock import patch

from app.routes import register_routes, BLUEPRINTS


# ==========================================================
# SUCCESS PATH
# ==========================================================


def test_register_routes_success():
    """
    Cover:
    - loop seluruh blueprint
    - register semua blueprint
    """

    app = Flask(__name__)

    registered = []

    def fake_register(bp):
        registered.append(bp)

    with patch.object(app, "register_blueprint", side_effect=fake_register):
        register_routes(app)

    assert registered == BLUEPRINTS
    assert len(registered) == len(BLUEPRINTS)


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
        side_effect=Exception("register failed"),
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
            side_effect=Exception("boom"),
        ):
            register_routes(app)

    assert mock_print.call_count == 2

    first_call = mock_print.call_args_list[0]
    second_call = mock_print.call_args_list[1]

    assert "ROUTE gagal di regis dan inisialisasi di create_app()" in first_call.args[0]

    assert second_call.args[0] == "ERROR:"
    assert str(second_call.args[1]) == "boom"


# ==========================================================
# VERIFY BLUEPRINT LIST
# ==========================================================


def test_blueprints_list_is_not_empty():
    """
    Memastikan BLUEPRINTS berisi blueprint yang akan diregister.
    """

    assert len(BLUEPRINTS) > 0


# ==========================================================
# VERIFY ALL BLUEPRINTS REGISTERED
# ==========================================================


def test_register_routes_registers_all_blueprints():

    app = Flask(__name__)

    count = 0

    def fake_register(_):
        nonlocal count
        count += 1

    with patch.object(app, "register_blueprint", side_effect=fake_register):
        register_routes(app)

    assert count == len(BLUEPRINTS)
