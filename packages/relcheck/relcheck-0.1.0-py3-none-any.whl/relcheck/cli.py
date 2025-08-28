import json
from typing import Optional

import click

from .core.types import CheckRegistry, Report, NoopMcpSolver
from .resources.pod import PodResource
from .core.kube import KubeContext
from .core.discovery import register_discovered_checks
from .resources.namespace import NamespaceResource
from .resources.cluster import ClusterResource
from .core.runner import run_resource
from .checks.data.configmap import ConfigMapSizeCheck
from .checks.data.secret import SecretTypeCheck
from .checks.data.pvc import PvcStorageClassCheck
from .checks.cluster.node import NodeReadyCheck

@click.group()
def main():
    """My CLI tool"""
    pass

@main.command()
@click.option("--resource-kind", type=click.Choice(["Pod", "Namespace", "Cluster"], case_sensitive=False), required=True)
@click.option("--namespace", default=None)
@click.option("--name", default=None)
@click.option("--format", "format_", type=click.Choice(["table", "json"], case_sensitive=False), default="table")
@click.option("--solve", is_flag=True, default=False, help="Populate solutions via MCP")
@click.option("--verbose", is_flag=True, default=False, help="Show both passed and failed checks")
@click.option("--deep", is_flag=True, default=False, help="Run checks on child resources as well")
@click.option("--kubeconfig", default=None, help="Path to kubeconfig")
@click.option("--context", "k8s_context", default=None, help="Kube context name")
def check_resource(resource_kind: str, namespace: Optional[str], name: Optional[str], format_: str, solve: bool, verbose: bool, deep: bool, kubeconfig: Optional[str], k8s_context: Optional[str]):
    """Run checks against a resource provided via file or flags (minimal demo)."""
    raw = {}

    registry = CheckRegistry()
    # keep a few base checks that don't need discovery (optional); then auto-discover
    registry.register("ConfigMap", ConfigMapSizeCheck())
    registry.register("Secret", SecretTypeCheck())
    registry.register("PersistentVolumeClaim", PvcStorageClassCheck())
    registry.register("Node", NodeReadyCheck())
    register_discovered_checks(registry)

    report = Report()
    kube_ctx = KubeContext(kubeconfig=kubeconfig, context=k8s_context)

    if resource_kind.lower() == "pod":
        if not name or not namespace:
            raise click.UsageError("For resource-kind Pod, --name and --namespace are required")
        # fetch live pod
        v1 = kube_ctx.core_v1()
        p = v1.read_namespaced_pod(name=name, namespace=namespace)
        raw = {
            "apiVersion": "v1",
            "kind": "Pod",
            "metadata": {"name": p.metadata.name, "namespace": p.metadata.namespace},
            "spec": {"containers": [c.to_dict() for c in (p.spec.containers or [])]},
        }
        res = PodResource.from_k8s_obj(raw, kube_context=kube_ctx)
        report.extend(run_resource(res, registry, deep=deep))
    elif resource_kind.lower() == "namespace":
        ns_name = name or namespace or "default"
        res = NamespaceResource.from_k8s_obj({"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": ns_name}}, kube_context=kube_ctx)
        report.extend(run_resource(res, registry, deep=deep))
    elif resource_kind.lower() == "cluster":
        res = ClusterResource.from_k8s_obj({"kind": "Cluster", "name": name or "cluster"}, kube_context=kube_ctx)
        report.extend(run_resource(res, registry, deep=deep))

    if solve:
        solver = NoopMcpSolver()  # placeholder; replace with real MCP integration
        report = solver.solve(report, resource_context={"resource": raw})

    if format_.lower() == "json":
        items = report.items if verbose else [i for i in report.items if not i.passed]
        click.echo(json.dumps([i.to_dict() for i in items], indent=2))
        return

    # table
    # build rows (filter failures unless verbose)
    headers = ["KIND", "NAMESPACE", "NAME", "CHECK", "TAG", "RESULT", "DETAILS"]
    items = report.items if verbose else [i for i in report.items if not i.passed]
    rows = []
    for i in items:
        tag = i.category
        tag_colored = click.style(tag.upper(), fg="yellow") if tag == "misconfig" else click.style(tag.upper(), fg="red")
        result = click.style("PASS", fg="green") if i.passed else click.style("FAIL", fg="red")
        rows.append([
            i.resource_kind,
            i.namespace or "",
            i.resource_name,
            f"{i.check_id}: {i.check_title}",
            tag_colored,
            result,
            i.details,
        ])

    data = [headers] + rows
    if not rows:
        click.echo("No issues found." if not verbose else "No checks to display.")
        return

    col_widths = [max(len(click.unstyle(str(row[i]))) for row in data) for i in range(len(headers))]

    def draw_border(sep: str = "-") -> str:
        parts = [sep * (w + 2) for w in col_widths]
        return "+" + "+".join(parts) + "+"

    def fmt_row(row):
        cells = []
        for i, val in enumerate(row):
            text = str(val)
            pad = col_widths[i] - len(click.unstyle(text))
            cells.append(" " + text + " " + (" " * pad))
        return "|" + "|".join(cells) + "|"

    click.echo(draw_border("-"))
    click.echo(fmt_row(headers))
    click.echo(draw_border("="))
    for r in rows:
        click.echo(fmt_row(r))
    click.echo(draw_border("-"))
