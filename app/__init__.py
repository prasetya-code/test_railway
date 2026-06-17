from flask import Flask
import traceback


def create_app():
    # initialize core
    # ===================
    core = Flask(__name__, static_folder="static", template_folder="templates")

    try:
        # register app extension
        # ===================
        from app.extensions import register_extension

        register_extension(core)

        # register config
        # ===================
        from config import register_config

        register_config(core)

        # # register app middleware
        # # ===================
        # from app.middleware import register_middleware

        # register_middleware(core)

        # register app routes
        # ===================
        from app.routes import register_routes

        register_routes(core)

    except Exception as e:
        print("\nFAILURE")
        print("ERROR:", e)

        traceback.print_exc()

    return core
