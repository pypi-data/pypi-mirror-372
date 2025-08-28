from __future__ import annotations

from ...core.types import ReportInfo, BaseCheck
from ...resources.workloads import DaemonSetResource


class DaemonSetTolerationsCheck(BaseCheck):
    id = "DS_TOLERATIONS"
    title = "DaemonSet should define appropriate tolerations"
    category = "misconfig"

    def run(self, resource: DaemonSetResource) -> ReportInfo:
        tolerations = (((resource.raw.get("spec", {}) or {}).get("template", {}) or {}).get("spec", {}) or {}).get("tolerations", [])
        passed = bool(tolerations)
        details = "tolerations present" if passed else "no tolerations defined"
        return ReportInfo(resource_kind=resource.kind, resource_name=resource.name, namespace=resource.namespace, check_id=self.id, check_title=self.title, category=self.category, passed=passed, details=details)


