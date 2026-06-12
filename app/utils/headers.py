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
            print(f"[DEBUG][registry] before-hook registered: {before.__module__}.{before.__qualname__}")

        if after:
            self.after_request_hooks.append(after)
            print(f"[DEBUG][registry] after-hook registered: {after.__module__}.{after.__qualname__}")


registry = HeaderRegistry()
print(f"[DEBUG] headers.py loaded as module: {__name__}, file={__file__}, registry id={id(registry)}")


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

        print(f"\n[DEBUG][before_request] path={request.path} method={request.method}")
        print(f"[DEBUG][before_request] total hooks={len(registry.before_request_hooks)}")

        for hook in registry.before_request_hooks:
            hook_name = f"{hook.__module__}.{hook.__qualname__}"
            try:
                try:
                    result = hook(request)
                except TypeError:
                    result = hook()

                print(f"[DEBUG][before_request] hook={hook_name} path={request.path} result={result}")

            except Exception:
                print(f"[DEBUG][before_request] hook={hook_name} path={request.path} ERROR:")
                traceback.print_exc()

    def after_request(self, response):
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        print(f"[DEBUG][after_request] path={request.path} method={request.method} elapsed_ms={elapsed_ms:.2f}")
        print(f"[DEBUG][after_request] total hooks={len(registry.after_request_hooks)}")

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

                print(f"[DEBUG][after_request] hook={hook_name} path={request.path} raw_result={result}")

                if not result or not isinstance(result, dict):
                    print(f"[DEBUG][after_request] hook={hook_name} path={request.path} -> SKIPPED (empty/non-dict)")
                    continue

                # detect module name if provided
                module_name = result.pop("__module__", None)
                priority = get_priority(module_name) if module_name else 0

                print(
                    f"[DEBUG][after_request] hook={hook_name} module={module_name} "
                    f"priority={priority} headers={result}"
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
                            f"[DEBUG][after_request] CONFLICT on '{k}': "
                            f"'{resolved_headers[k]}' (prio={resolved_priority[k]}) "
                            f"-> '{v}' (prio={priority}) [module={module_name}]"
                        )
                        resolved_headers[k] = v
                        resolved_priority[k] = priority
                    else:
                        print(
                            f"[DEBUG][after_request] CONFLICT on '{k}': "
                            f"kept '{resolved_headers[k]}' (prio={resolved_priority[k]}), "
                            f"ignored '{v}' (prio={priority}) [module={module_name}]"
                        )

            except Exception:
                print(f"[DEBUG][after_request] hook={hook_name} path={request.path} ERROR:")
                traceback.print_exc()

        print(f"[DEBUG][after_request] path={request.path} FINAL resolved_headers={resolved_headers}")

        # apply headers
        try:
            for k, v in resolved_headers.items():
                response.headers[k] = v
        except Exception:
            print(f"[DEBUG][after_request] path={request.path} ERROR applying headers:")
            traceback.print_exc()

        return response


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------


def init_headers(app):
    print("[DEBUG] init_headers: initializing header orchestrator")

    orchestrator = HeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    print("[DEBUG] init_headers: before_request and after_request hooks registered")
    print(
        f"[DEBUG] init_headers: registered before-hooks={len(registry.before_request_hooks)}, "
        f"after-hooks={len(registry.after_request_hooks)}"
    )

    return orchestrator