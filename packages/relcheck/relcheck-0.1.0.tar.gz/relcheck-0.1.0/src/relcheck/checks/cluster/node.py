from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.nodes import NodeResource


class NodeReadyCheck(BaseCheck):
    id = "NODE_READY"
    title = "Node should be Ready"
    category = "fault"

    def run(self, resource: NodeResource) -> ReportInfo:
        conds = (resource.raw.get("status", {}) or {}).get("conditions", [])
        ready = any((c.get("type") == "Ready" and c.get("status") == "True") for c in conds)
        passed = bool(ready)
        details = "Ready=True" if passed else "Node not Ready"
        return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=None, check_id=self.id, check_title=self.title, category=self.category, passed=passed, details=details)


