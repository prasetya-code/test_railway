"""
Cross-Origin Isolation Headers Policy

Handles:
- Cross-Origin-Opener-Policy (COOP)
- Cross-Origin-Embedder-Policy (COEP)
- Cross-Origin-Resource-Policy (CORP)
- Origin-Agent-Cluster

Purpose:
- Enable cross-origin isolation for SharedArrayBuffer
- Improve process isolation and memory safety
"""

from app.utils.headers import registry


# ---------------------------------------------------------------------------
# POLICY LAYER
# ---------------------------------------------------------------------------


class IsolationHeaderPolicy:
    COOP_POLICY = "same-origin"
    COEP_POLICY = "require-corp"
    CORP_POLICY = "same-origin"

    ORIGIN_AGENT_CLUSTER = True
    REPORT_TO = None

    PRESET = None  # full | credentialless | none


# ---------------------------------------------------------------------------
# HEADER BUILDERS
# ---------------------------------------------------------------------------


def build_coop_header(policy, report_to=None):
    headers = {"Cross-Origin-Opener-Policy": policy}

    if report_to:
        headers["Cross-Origin-Opener-Policy-Report-Only"] = (
            f"{policy}; report-to={report_to}"
        )

    return headers


def build_coep_header(policy, report_to=None):
    headers = {"Cross-Origin-Embedder-Policy": policy}

    if report_to:
        headers["Cross-Origin-Embedder-Policy-Report-Only"] = (
            f"{policy}; report-to={report_to}"
        )

    return headers


def build_corp_header(policy):
    return {"Cross-Origin-Resource-Policy": policy}


def build_origin_agent_cluster_header(enable):
    return {"Origin-Agent-Cluster": "?1" if enable else "?0"}


def build_observability_headers(elapsed_ms):
    return {"X-Response-Time": f"{elapsed_ms:.2f}ms"}


# ---------------------------------------------------------------------------
# PRESETS
# ---------------------------------------------------------------------------


def preset_full_isolation():
    return {
        "coop": "same-origin",
        "coep": "require-corp",
        "corp": "same-origin",
        "oac": True,
    }


def preset_credentialless_isolation():
    return {
        "coop": "same-origin",
        "coep": "credentialless",
        "corp": "same-origin",
        "oac": True,
    }


def preset_no_isolation():
    return {
        "coop": "unsafe-none",
        "coep": "unsafe-none",
        "corp": "cross-origin",
        "oac": False,
    }


# ---------------------------------------------------------------------------
# PLUGIN INITIALIZER (NO ORCHESTRATOR)
# ---------------------------------------------------------------------------


def init_isolation_headers():

    def before():
        # reserved for future context
        pass

    def after(elapsed_ms):
        headers = {}

        preset = IsolationHeaderPolicy.PRESET

        # -------------------------
        # PRESET MODE
        # -------------------------
        if preset == "full":
            config = preset_full_isolation()

        elif preset == "credentialless":
            config = preset_credentialless_isolation()

        elif preset == "none":
            config = preset_no_isolation()

        # -------------------------
        # MANUAL MODE
        # -------------------------
        else:
            config = {
                "coop": IsolationHeaderPolicy.COOP_POLICY,
                "coep": IsolationHeaderPolicy.COEP_POLICY,
                "corp": IsolationHeaderPolicy.CORP_POLICY,
                "oac": IsolationHeaderPolicy.ORIGIN_AGENT_CLUSTER,
            }

        # COOP
        headers.update(
            build_coop_header(
                config["coop"],
                IsolationHeaderPolicy.REPORT_TO,
            )
        )

        # COEP
        headers.update(
            build_coep_header(
                config["coep"],
                IsolationHeaderPolicy.REPORT_TO,
            )
        )

        # CORP
        headers.update(build_corp_header(config["corp"]))

        # Origin Agent Cluster
        headers.update(build_origin_agent_cluster_header(config["oac"]))

        # Observability
        headers.update(build_observability_headers(elapsed_ms))

        headers["__module__"] = "isolation"

        return headers
    
    print(f"[DEBUG][isolation] using registry id={id(registry)} from module={registry.__class__.__module__}")

    registry.register(before=before, after=after)
