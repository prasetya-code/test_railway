import time
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

        for hook in registry.before_request_hooks:
            try:
                hook(request)
            except TypeError:
                hook()

    def after_request(self, response):
        elapsed_ms = (time.perf_counter() - self.start_time) * 1000

        # final resolved headers (priority-aware)
        resolved_headers = {}
        resolved_priority = {}

        for hook in registry.after_request_hooks:
            try:
                result = hook(request, response, elapsed_ms)
            except TypeError:
                try:
                    result = hook(request, elapsed_ms)
                except TypeError:
                    result = hook(elapsed_ms)

            if not result or not isinstance(result, dict):
                continue

            # detect module name if provided
            module_name = result.pop("__module__", None)
            priority = get_priority(module_name) if module_name else 0

            for k, v in result.items():

                # if key not exists → accept
                if k not in resolved_headers:
                    resolved_headers[k] = v
                    resolved_priority[k] = priority
                    continue

                # if same key exists → resolve by priority
                if priority >= resolved_priority[k]:
                    resolved_headers[k] = v
                    resolved_priority[k] = priority

        # apply headers
        for k, v in resolved_headers.items():
            response.headers[k] = v

        return response


# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------

def register_headers(app):

    orchestrator = HeaderOrchestrator(app)

    app.before_request(orchestrator.before_request)
    app.after_request(orchestrator.after_request)

    return orchestrator