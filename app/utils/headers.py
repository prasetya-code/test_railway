import time
import traceback
from flask import request


# ---------------------------------------------------------------------------
# HEADER REGISTRY
# ---------------------------------------------------------------------------


class HeaderRegistry:
    def __init__(self):
        self.before_request_hooks = []
        self.after_request_hooks = []

    def register(self, before=None, after=None):
        if before:
            self.before_request_hooks.append(before)

        if after:
            self.after_request_hooks.append(after)


registry = HeaderRegistry()


# ---------------------------------------------------------------------------
# PRIORITY SYSTEM
# higher number = stronger priority (wins conflict)
# ---------------------------------------------------------------------------

HEADER_PRIORITY = {
    # security core layers
    "csp": 100,
    "isolation": 90,
    # cross origin
    "cors": 80,
    # caching layer
    "cache": 70,
    # browser hardening
    "browser": 60,
    # general hardening
    "hardening": 50,
    # api / metadata
    "api": 40,
}


def get_priority(module_name: str) -> int:
    return HEADER_PRIORITY.get(module_name, 0)


# ---------------------------------------------------------------------------
# SINGLE ORCHESTRATOR
# ---------------------------------------------------------------------------


class HeaderOrchestrator:
    def __init__(self, app):
        self.app = app
        self.start_time = None

    def before_request(self):
        self.start_time = time.perf_counter()

        request.headers_context = getattr(request, "headers_context", {})

        print(f"\n[Orchestrator][before]: "
              f"path = {request.path}, method = {request.method}, total hooks = {len(registry.before_request_hooks)} \n")

        for hook in registry.before_request_hooks:
            hook_name = f"{hook.__module__}.{hook.__qualname__}"
            try:
                try:
                    result = hook(request)
                except TypeError:
                    result = hook()

                print(f"[DEBUG][before_request] path = {request.path}, hook = {hook_name}, result = {result}")

            except Exception:
                print(f"[DEBUG][before_request] path = {request.path}, hook = {hook_name}, ERROR:")
                traceback.print_exc()

    def after_request(self, response):
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        print(f"\n[Orchestrator][after]: "
              f"path = {request.path}, method = {request.method}, elapsed_ms = {elapsed_ms:.2f}, total hooks = {len(registry.after_request_hooks)} \n")

        # final resolved headers (priority-aware)
        resolved_headers = {}
        resolved_priority = {}

        for hook in registry.after_request_hooks:
            hook_name = f"{hook.__module__}.{hook.__qualname__}"
            try:
                try:
                    result = hook(request, response, elapsed_ms)

                except TypeError:
                    try:
                        result = hook(request, elapsed_ms)

                    except TypeError:
                        result = hook(elapsed_ms)

                print(f"[DEBUG][resolved headers] path = {request.path}, hook = {hook_name}")

                if not result or not isinstance(result, dict):
                    print(f"SKIPPED: path = {request.path} hook = {hook_name} -> (empty/non-dict)")
                    continue

                # detect module name if provided
                module_name = result.pop("__module__", None)
                priority = get_priority(module_name) if module_name else 0

                print(
                    f"[PRIORITY][detect module] "
                    f"priority = {priority}, "
                    # f"headers = {result}, "
                    # f"hook = {hook_name}, "
                    f"module = {module_name} \n"
                )

                for k, v in result.items():
                    # if key not exists → accept
                    if k not in resolved_headers:
                        resolved_headers[k] = v
                        resolved_priority[k] = priority
                        continue

                    # if same key exists → resolve by priority
                    if priority >= resolved_priority[k]:
                        print(
                            f"[CONFLICT][same key exists] on '{k}': "
                            f"'{resolved_headers[k]}' (prio = {resolved_priority[k]}) "
                            f"-> '{v}' (prio = {priority}) [module = {module_name}]"
                        )
                        resolved_headers[k] = v
                        resolved_priority[k] = priority
                    else:
                        print(
                            f"[CONFLICT][resolve by priority] CONFLICT on '{k}': "
                            f"kept '{resolved_headers[k]}' (prio={resolved_priority[k]}), "
                            f"ignored '{v}' (prio={priority}) [module={module_name}]"
                        )

            except Exception:
                print(f"[DEBUG][after_request] path={request.path}, hook={hook_name}, ERROR:")
                traceback.print_exc()

        # print(f"\n[FINAL] path={request.path}  resolved_headers={resolved_headers}")

        # apply headers
        try:
            for k, v in resolved_headers.items():
                response.headers[k] = v

        except Exception:
            print(f"[DEBUG][after_request] path={request.path} ERROR applying headers:")
            traceback.print_exc()

        return response


# =============================================================================
# ENTRY POINT
# =============================================================================

def init_headers(app):
    print("[HEADERS] initializing header orchestrator \n")

    # import di sini (lazy import) untuk hindari circular import,
    # karena modul-modul ini sendiri mengimport `registry` dari headers.py
    from .headers_policy.api import init_api_headers
    from .headers_policy.browser import init_browser_headers
    from .headers_policy.cache import init_cache_headers
    from .headers_policy.cors import init_cors_headers
    from .headers_policy.csp import init_csp_headers
    from .headers_policy.hardening import init_hardening_headers
    from .headers_policy.isolation import init_isolation_headers

    # daftarkan semua header policy ke registry
    init_csp_headers()
    init_isolation_headers()
    init_cors_headers()
    init_cache_headers()
    init_browser_headers()
    init_hardening_headers()
    init_api_headers()

    orchestrator = HeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    print(f"\n[HEADERS] initialize hooks: "
        f"before-hooks = {len(registry.before_request_hooks)}, "
        f"after-hooks = {len(registry.after_request_hooks)} \n"
    )

    return orchestrator