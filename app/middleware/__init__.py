import traceback


def register_middleware(app):
    try:
        from .nonce import init_nonce
        # from .headers import init_headers

        init_nonce(app)
        # init_headers(app)

    except Exception as e:
        print("\nUTILS gagal di regis dan inisialisasi di create_app()")
        print("ERROR:", e)

        traceback.print_exc()
