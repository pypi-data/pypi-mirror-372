#!/usr/bin/env python3
"""
DORA Metrics Engine for HITL System Optimization

Issue #93: HITL System & DORA Metrics Optimization
Priority: High (Sprint 1 Improvements)
Scope: Optimize Human-in-the-Loop system and enhance DORA metrics collection
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..utils.logger import configure_logger

logger = configure_logger(__name__)


@dataclass
class DORAMetric:
    """Individual DORA metric measurement"""

    metric_name: str
    value: float
    unit: str
    timestamp: datetime
    tags: Dict[str, str] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class DeploymentEvent:
    """Deployment event for DORA metrics tracking"""

    deployment_id: str
    environment: str
    service_name: str
    version: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: str = "in_progress"  # in_progress, success, failed, rolled_back
    commit_sha: str = ""
    approver: str = ""
    rollback_time: Optional[datetime] = None


@dataclass
class IncidentEvent:
    """Incident event for DORA metrics tracking"""

    incident_id: str
    service_name: str
    severity: str  # critical, high, medium, low
    start_time: datetime
    detection_time: Optional[datetime] = None
    resolution_time: Optional[datetime] = None
    root_cause: str = ""
    caused_by_deployment: str = ""


class DORAMetricsEngine:
    """Enhanced DORA metrics collection and analysis engine"""

    def __init__(self, artifacts_dir: str = "./artifacts/metrics", cross_validation_tolerance: float = 15.0):
        """
        Initialize DORA metrics engine

        Args:
            artifacts_dir: Directory to store metrics artifacts
            cross_validation_tolerance: Tolerance percentage for metric validation
        """
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)

        self.tolerance = cross_validation_tolerance

        # Metrics storage
        self.deployments: List[DeploymentEvent] = []
        self.incidents: List[IncidentEvent] = []
        self.metrics_history: List[DORAMetric] = []

        # HITL workflow metrics
        self.approval_times: List[float] = []
        self.workflow_bottlenecks: Dict[str, List[float]] = {}

        # Performance targets from CLAUDE.md
        self.targets = {
            "lead_time_hours": 4,  # <4 hours
            "deploy_frequency_daily": 1,  # Daily deployment capability
            "change_failure_rate": 0.05,  # <5%
            "mttr_hours": 1,  # <1 hour
            "approval_time_minutes": 30,  # <30 minutes
            "success_rate": 0.95,  # >95%
        }

    def record_deployment(
        self,
        deployment_id: str,
        environment: str,
        service_name: str,
        version: str,
        commit_sha: str = "",
        approver: str = "",
    ) -> DeploymentEvent:
        """Record a new deployment event"""

        deployment = DeploymentEvent(
            deployment_id=deployment_id,
            environment=environment,
            service_name=service_name,
            version=version,
            start_time=datetime.now(timezone.utc),
            commit_sha=commit_sha,
            approver=approver,
        )

        self.deployments.append(deployment)

        logger.info(f"🚀 Deployment recorded: {deployment_id} for {service_name}")

        return deployment

    def complete_deployment(self, deployment_id: str, status: str, rollback_time: Optional[datetime] = None) -> bool:
        """Mark deployment as complete"""

        for deployment in self.deployments:
            if deployment.deployment_id == deployment_id:
                deployment.end_time = datetime.now(timezone.utc)
                deployment.status = status
                deployment.rollback_time = rollback_time

                logger.info(f"✅ Deployment completed: {deployment_id} - {status}")
                return True

        logger.warning(f"⚠️ Deployment not found: {deployment_id}")
        return False

    def record_incident(
        self, incident_id: str, service_name: str, severity: str, root_cause: str = "", caused_by_deployment: str = ""
    ) -> IncidentEvent:
        """Record a new incident event"""

        incident = IncidentEvent(
            incident_id=incident_id,
            service_name=service_name,
            severity=severity,
            start_time=datetime.now(timezone.utc),
            root_cause=root_cause,
            caused_by_deployment=caused_by_deployment,
        )

        self.incidents.append(incident)

        logger.info(f"🚨 Incident recorded: {incident_id} - {severity} severity")

        return incident

    def resolve_incident(self, incident_id: str, detection_time: Optional[datetime] = None) -> bool:
        """Mark incident as resolved"""

        for incident in self.incidents:
            if incident.incident_id == incident_id:
                incident.resolution_time = datetime.now(timezone.utc)
                if detection_time:
                    incident.detection_time = detection_time

                logger.info(f"✅ Incident resolved: {incident_id}")
                return True

        logger.warning(f"⚠️ Incident not found: {incident_id}")
        return False

    def record_approval_time(self, approval_time_minutes: float, workflow_step: str = "general"):
        """Record HITL approval time"""
        self.approval_times.append(approval_time_minutes)

        if workflow_step not in self.workflow_bottlenecks:
            self.workflow_bottlenecks[workflow_step] = []
        self.workflow_bottlenecks[workflow_step].append(approval_time_minutes)

    def calculate_lead_time(self, days_back: int = 30) -> DORAMetric:
        """Calculate deployment lead time"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_deployments = [d for d in self.deployments if d.start_time >= cutoff_date and d.end_time]

        if not recent_deployments:
            return DORAMetric(
                metric_name="lead_time",
                value=0.0,
                unit="hours",
                timestamp=datetime.now(timezone.utc),
                tags={"period": f"{days_back}d", "status": "no_data"},
            )

        # Calculate average lead time (simplified - in real scenario would track from commit to production)
        lead_times = []
        for deployment in recent_deployments:
            if deployment.end_time and deployment.status == "success":
                duration = (deployment.end_time - deployment.start_time).total_seconds() / 3600  # hours
                lead_times.append(duration)

        avg_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0

        metric = DORAMetric(
            metric_name="lead_time",
            value=avg_lead_time,
            unit="hours",
            timestamp=datetime.now(timezone.utc),
            tags={
                "period": f"{days_back}d",
                "deployments_count": str(len(recent_deployments)),
                "successful_deployments": str(len(lead_times)),
            },
            metadata={
                "target": self.targets["lead_time_hours"],
                "target_met": avg_lead_time <= self.targets["lead_time_hours"],
            },
        )

        self.metrics_history.append(metric)
        return metric

    def calculate_deployment_frequency(self, days_back: int = 30) -> DORAMetric:
        """Calculate deployment frequency"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_deployments = [d for d in self.deployments if d.start_time >= cutoff_date]

        # Calculate deployments per day
        deployments_per_day = len(recent_deployments) / days_back if days_back > 0 else 0

        metric = DORAMetric(
            metric_name="deployment_frequency",
            value=deployments_per_day,
            unit="deployments_per_day",
            timestamp=datetime.now(timezone.utc),
            tags={"period": f"{days_back}d", "total_deployments": str(len(recent_deployments))},
            metadata={
                "target": self.targets["deploy_frequency_daily"],
                "target_met": deployments_per_day >= self.targets["deploy_frequency_daily"],
            },
        )

        self.metrics_history.append(metric)
        return metric

    def calculate_change_failure_rate(self, days_back: int = 30) -> DORAMetric:
        """Calculate change failure rate"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_deployments = [d for d in self.deployments if d.start_time >= cutoff_date and d.end_time]

        if not recent_deployments:
            return DORAMetric(
                metric_name="change_failure_rate",
                value=0.0,
                unit="percentage",
                timestamp=datetime.now(timezone.utc),
                tags={"period": f"{days_back}d", "status": "no_data"},
            )

        failed_deployments = len([d for d in recent_deployments if d.status in ["failed", "rolled_back"]])

        failure_rate = failed_deployments / len(recent_deployments)

        metric = DORAMetric(
            metric_name="change_failure_rate",
            value=failure_rate,
            unit="percentage",
            timestamp=datetime.now(timezone.utc),
            tags={
                "period": f"{days_back}d",
                "total_deployments": str(len(recent_deployments)),
                "failed_deployments": str(failed_deployments),
            },
            metadata={
                "target": self.targets["change_failure_rate"],
                "target_met": failure_rate <= self.targets["change_failure_rate"],
            },
        )

        self.metrics_history.append(metric)
        return metric

    def calculate_mttr(self, days_back: int = 30) -> DORAMetric:
        """Calculate Mean Time to Recovery (MTTR)"""

        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_back)
        recent_incidents = [i for i in self.incidents if i.start_time >= cutoff_date and i.resolution_time]

        if not recent_incidents:
            return DORAMetric(
                metric_name="mttr",
                value=0.0,
                unit="hours",
                timestamp=datetime.now(timezone.utc),
                tags={"period": f"{days_back}d", "status": "no_data"},
            )

        # Calculate recovery times
        recovery_times = []
        for incident in recent_incidents:
            if incident.resolution_time:
                duration = (incident.resolution_time - incident.start_time).total_seconds() / 3600  # hours
                recovery_times.append(duration)

        avg_mttr = sum(recovery_times) / len(recovery_times) if recovery_times else 0

        metric = DORAMetric(
            metric_name="mttr",
            value=avg_mttr,
            unit="hours",
            timestamp=datetime.now(timezone.utc),
            tags={"period": f"{days_back}d", "incidents_count": str(len(recent_incidents))},
            metadata={"target": self.targets["mttr_hours"], "target_met": avg_mttr <= self.targets["mttr_hours"]},
        )

        self.metrics_history.append(metric)
        return metric

    def calculate_hitl_metrics(self) -> Dict[str, DORAMetric]:
        """Calculate Human-in-the-Loop specific metrics"""

        metrics = {}

        # Average approval time
        if self.approval_times:
            avg_approval_time = sum(self.approval_times) / len(self.approval_times)

            metrics["approval_time"] = DORAMetric(
                metric_name="approval_time",
                value=avg_approval_time,
                unit="minutes",
                timestamp=datetime.now(timezone.utc),
                tags={"total_approvals": str(len(self.approval_times))},
                metadata={
                    "target": self.targets["approval_time_minutes"],
                    "target_met": avg_approval_time <= self.targets["approval_time_minutes"],
                },
            )

        # Workflow bottlenecks analysis
        if self.workflow_bottlenecks:
            bottleneck_metrics = {}

            for step, times in self.workflow_bottlenecks.items():
                if times:
                    avg_time = sum(times) / len(times)
                    bottleneck_metrics[f"{step}_avg_time"] = avg_time

            # Identify slowest step
            if bottleneck_metrics:
                slowest_step = max(bottleneck_metrics, key=bottleneck_metrics.get)
                slowest_time = bottleneck_metrics[slowest_step]

                metrics["workflow_bottleneck"] = DORAMetric(
                    metric_name="workflow_bottleneck",
                    value=slowest_time,
                    unit="minutes",
                    timestamp=datetime.now(timezone.utc),
                    tags={"bottleneck_step": slowest_step},
                    metadata={"all_steps": bottleneck_metrics},
                )

        return metrics

    def generate_comprehensive_report(self, days_back: int = 30) -> Dict:
        """Generate comprehensive DORA metrics report"""

        logger.info(f"📊 Generating DORA metrics report for last {days_back} days")

        # Calculate all DORA metrics
        lead_time = self.calculate_lead_time(days_back)
        deployment_freq = self.calculate_deployment_frequency(days_back)
        failure_rate = self.calculate_change_failure_rate(days_back)
        mttr = self.calculate_mttr(days_back)

        # Calculate HITL metrics
        hitl_metrics = self.calculate_hitl_metrics()

        # Performance analysis
        targets_met = {
            "lead_time": lead_time.metadata.get("target_met", False),
            "deployment_frequency": deployment_freq.metadata.get("target_met", False),
            "change_failure_rate": failure_rate.metadata.get("target_met", False),
            "mttr": mttr.metadata.get("target_met", False),
        }

        # Add HITL targets
        if "approval_time" in hitl_metrics:
            targets_met["approval_time"] = hitl_metrics["approval_time"].metadata.get("target_met", False)

        overall_performance = sum(targets_met.values()) / len(targets_met) * 100

        report = {
            "report_type": "dora_metrics_comprehensive",
            "period": f"{days_back}_days",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "dora_metrics": {
                "lead_time": asdict(lead_time),
                "deployment_frequency": asdict(deployment_freq),
                "change_failure_rate": asdict(failure_rate),
                "mttr": asdict(mttr),
            },
            "hitl_metrics": {k: asdict(v) for k, v in hitl_metrics.items()},
            "performance_analysis": {
                "targets_met": targets_met,
                "overall_performance_percentage": overall_performance,
                "performance_grade": self._calculate_performance_grade(overall_performance),
            },
            "recommendations": self._generate_recommendations(targets_met, hitl_metrics),
            "raw_data": {
                "deployments_count": len(self.deployments),
                "incidents_count": len(self.incidents),
                "approval_times_count": len(self.approval_times),
            },
        }

        # Save report
        report_file = self.artifacts_dir / f"dora_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"✅ DORA metrics report saved to: {report_file}")

        return report

    def _calculate_performance_grade(self, percentage: float) -> str:
        """Calculate performance grade based on targets met"""
        if percentage >= 90:
            return "A (Excellent)"
        elif percentage >= 80:
            return "B (Good)"
        elif percentage >= 70:
            return "C (Satisfactory)"
        elif percentage >= 60:
            return "D (Needs Improvement)"
        else:
            return "F (Poor)"

    def _generate_recommendations(self, targets_met: Dict[str, bool], hitl_metrics: Dict) -> List[str]:
        """Generate recommendations based on metrics analysis"""

        recommendations = []

        if not targets_met.get("lead_time", False):
            recommendations.append(
                "🎯 Optimize lead time: Consider parallel workflows, automated testing, and faster approval processes"
            )

        if not targets_met.get("deployment_frequency", False):
            recommendations.append(
                "🚀 Increase deployment frequency: Implement continuous deployment pipeline and smaller batch sizes"
            )

        if not targets_met.get("change_failure_rate", False):
            recommendations.append(
                "🛡️ Reduce failure rate: Enhance testing coverage, implement canary deployments, and improve rollback procedures"
            )

        if not targets_met.get("mttr", False):
            recommendations.append(
                "⚡ Improve MTTR: Enhance monitoring, implement automated incident response, and improve alerting"
            )

        if not targets_met.get("approval_time", False):
            recommendations.append(
                "⏰ Optimize approval workflow: Streamline HITL processes, implement parallel approvals, and reduce approval steps"
            )

        # HITL-specific recommendations
        if "workflow_bottleneck" in hitl_metrics:
            bottleneck_step = hitl_metrics["workflow_bottleneck"].tags.get("bottleneck_step", "unknown")
            recommendations.append(f"🔍 Address workflow bottleneck: Focus on optimizing '{bottleneck_step}' step")

        if not recommendations:
            recommendations.append(
                "✅ All targets met! Consider raising performance targets or exploring advanced optimization opportunities"
            )

        return recommendations

    def export_metrics_for_visualization(self, output_file: Optional[str] = None) -> str:
        """Export metrics in format suitable for visualization tools"""

        if not output_file:
            output_file = self.artifacts_dir / f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        export_data = {
            "export_timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics_history": [asdict(m) for m in self.metrics_history],
            "deployments": [asdict(d) for d in self.deployments],
            "incidents": [asdict(i) for i in self.incidents],
            "targets": self.targets,
            "summary_stats": {
                "total_deployments": len(self.deployments),
                "successful_deployments": len([d for d in self.deployments if d.status == "success"]),
                "total_incidents": len(self.incidents),
                "resolved_incidents": len([i for i in self.incidents if i.resolution_time]),
                "average_approval_time": sum(self.approval_times) / len(self.approval_times)
                if self.approval_times
                else 0,
            },
        }

        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"📊 Metrics exported for visualization: {output_file}")
        return str(output_file)


# Async functions for integration with existing systems
async def simulate_dora_metrics_collection(duration_minutes: int = 5) -> Dict:
    """Simulate DORA metrics collection for demonstration"""

    engine = DORAMetricsEngine()

    logger.info(f"🧪 Starting {duration_minutes}-minute DORA metrics simulation")

    # Simulate deployment events
    deployments = [
        ("deploy-001", "production", "vpc-wrapper", "v1.2.0", "abc123", "manager"),
        ("deploy-002", "staging", "finops-dashboard", "v2.1.0", "def456", "architect"),
        ("deploy-003", "production", "organizations-api", "v1.0.1", "ghi789", "manager"),
    ]

    for dep_id, env, service, version, commit, approver in deployments:
        deployment = engine.record_deployment(dep_id, env, service, version, commit, approver)

        # Simulate approval time
        approval_time = 15 + (hash(dep_id) % 30)  # 15-45 minutes
        engine.record_approval_time(approval_time, f"{env}_deployment")

        # Simulate deployment completion after short delay
        await asyncio.sleep(1)

        # 90% success rate simulation
        status = "success" if hash(dep_id) % 10 < 9 else "failed"
        engine.complete_deployment(dep_id, status)

    # Simulate incidents
    incidents = [
        ("inc-001", "vpc-wrapper", "high", "Network configuration error", "deploy-001"),
        ("inc-002", "finops-dashboard", "medium", "Query timeout", ""),
    ]

    for inc_id, service, severity, cause, caused_by in incidents:
        incident = engine.record_incident(inc_id, service, severity, cause, caused_by)

        # Simulate incident resolution
        await asyncio.sleep(0.5)
        detection_time = incident.start_time + timedelta(minutes=5)
        engine.resolve_incident(inc_id, detection_time)

    # Generate comprehensive report
    report = engine.generate_comprehensive_report(days_back=7)

    return report


if __name__ == "__main__":
    # CLI execution
    import argparse

    parser = argparse.ArgumentParser(description="DORA Metrics Engine")
    parser.add_argument("--simulate", action="store_true", help="Run simulation mode")
    parser.add_argument("--duration", type=int, default=5, help="Simulation duration in minutes")
    parser.add_argument("--output", "-o", default="./artifacts/metrics", help="Output directory for metrics")

    args = parser.parse_args()

    async def main():
        if args.simulate:
            report = await simulate_dora_metrics_collection(args.duration)
            print("✅ DORA metrics simulation completed")
            print(f"📊 Overall performance: {report['performance_analysis']['performance_grade']}")
            print(
                f"🎯 Targets met: {sum(report['performance_analysis']['targets_met'].values())}/{len(report['performance_analysis']['targets_met'])}"
            )
        else:
            engine = DORAMetricsEngine(args.output)
            report = engine.generate_comprehensive_report()
            print("✅ DORA metrics report generated")
            print(f"📊 Report saved to: {engine.artifacts_dir}")

    asyncio.run(main())
