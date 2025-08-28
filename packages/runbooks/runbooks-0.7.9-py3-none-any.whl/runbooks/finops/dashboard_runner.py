import argparse
import os
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import boto3
from rich import box
from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn, track
from rich.status import Status
from rich.table import Column, Table

from runbooks.finops.aws_client import (
    ec2_summary,
    get_accessible_regions,
    get_account_id,
    get_aws_profiles,
    get_budgets,
    get_stopped_instances,
    get_untagged_resources,
    get_unused_eips,
    get_unused_volumes,
)
from runbooks.finops.cost_processor import (
    change_in_total_cost,
    export_to_csv,
    export_to_json,
    format_budget_info,
    format_ec2_summary,
    get_cost_data,
    get_trend,
    process_service_costs,
)
from runbooks.finops.helpers import (
    clean_rich_tags,
    export_audit_report_to_csv,
    export_audit_report_to_json,
    export_audit_report_to_pdf,
    export_cost_dashboard_to_pdf,
    export_trend_data_to_json,
    generate_pdca_improvement_report,
)
from runbooks.finops.profile_processor import (
    process_combined_profiles,
    process_single_profile,
)
from runbooks.finops.types import ProfileData
from runbooks.finops.visualisations import create_trend_bars

console = Console()


def _get_profile_for_operation(operation_type: str, default_profile: str) -> str:
    """
    Get the appropriate AWS profile based on operation type.

    Args:
        operation_type: Type of operation ('billing', 'management', 'operational')
        default_profile: Default profile to fall back to

    Returns:
        str: Profile name to use for the operation
    """
    profile_map = {
        "billing": os.getenv("BILLING_PROFILE"),
        "management": os.getenv("MANAGEMENT_PROFILE"),
        "operational": os.getenv("CENTRALISED_OPS_PROFILE"),
    }

    profile = profile_map.get(operation_type)
    if profile:
        # Verify profile exists
        available_profiles = boto3.Session().available_profiles
        if profile in available_profiles:
            console.log(f"[dim cyan]Using {operation_type} profile: {profile}[/]")
            return profile
        else:
            console.log(
                f"[yellow]Warning: {operation_type.title()} profile '{profile}' not found in AWS config. Using default: {default_profile}[/]"
            )

    return default_profile


def _create_cost_session(profile: str) -> boto3.Session:
    """
    Create a boto3 session specifically for cost operations.
    Uses BILLING_PROFILE if available, falls back to provided profile.

    Args:
        profile: Default profile to use

    Returns:
        boto3.Session: Session configured for cost operations
    """
    cost_profile = _get_profile_for_operation("billing", profile)
    return boto3.Session(profile_name=cost_profile)


def _create_management_session(profile: str) -> boto3.Session:
    """
    Create a boto3 session specifically for management operations.
    Uses MANAGEMENT_PROFILE if available, falls back to provided profile.

    Args:
        profile: Default profile to use

    Returns:
        boto3.Session: Session configured for management operations
    """
    mgmt_profile = _get_profile_for_operation("management", profile)
    return boto3.Session(profile_name=mgmt_profile)


def _create_operational_session(profile: str) -> boto3.Session:
    """
    Create a boto3 session specifically for operational tasks.
    Uses CENTRALISED_OPS_PROFILE if available, falls back to provided profile.

    Args:
        profile: Default profile to use

    Returns:
        boto3.Session: Session configured for operational tasks
    """
    ops_profile = _get_profile_for_operation("operational", profile)
    return boto3.Session(profile_name=ops_profile)


def _calculate_risk_score(untagged, stopped, unused_vols, unused_eips, budget_data):
    """Calculate risk score based on audit findings for PDCA tracking."""
    score = 0

    # Untagged resources (high risk for compliance)
    untagged_count = sum(len(ids) for region_map in untagged.values() for ids in region_map.values())
    score += untagged_count * 2  # High weight for untagged

    # Stopped instances (medium risk for cost)
    stopped_count = sum(len(ids) for ids in stopped.values())
    score += stopped_count * 1

    # Unused volumes (medium risk for cost)
    volume_count = sum(len(ids) for ids in unused_vols.values())
    score += volume_count * 1

    # Unused EIPs (high risk for cost)
    eip_count = sum(len(ids) for ids in unused_eips.values())
    score += eip_count * 3  # High cost impact

    # Budget overruns (critical risk)
    overruns = len([b for b in budget_data if b["actual"] > b["limit"]])
    score += overruns * 5  # Critical weight

    return score


def _format_risk_score(score):
    """Format risk score with visual indicators."""
    if score == 0:
        return "[bright_green]🟢 LOW\n(0)[/]"
    elif score <= 10:
        return f"[yellow]🟡 MEDIUM\n({score})[/]"
    elif score <= 25:
        return f"[orange1]🟠 HIGH\n({score})[/]"
    else:
        return f"[bright_red]🔴 CRITICAL\n({score})[/]"


def _display_pdca_summary(pdca_metrics):
    """Display PDCA improvement summary with actionable insights."""
    if not pdca_metrics:
        return

    total_risk = sum(m["risk_score"] for m in pdca_metrics)
    avg_risk = total_risk / len(pdca_metrics)

    high_risk_accounts = [m for m in pdca_metrics if m["risk_score"] > 25]
    total_untagged = sum(m["untagged_count"] for m in pdca_metrics)
    total_unused_eips = sum(m["unused_eips_count"] for m in pdca_metrics)

    summary_table = Table(title="🎯 PDCA Continuous Improvement Metrics", box=box.SIMPLE, style="cyan")
    summary_table.add_column("Metric", style="bold")
    summary_table.add_column("Value", justify="right")
    summary_table.add_column("Action Required", style="yellow")

    summary_table.add_row("Average Risk Score", f"{avg_risk:.1f}", "✅ Good" if avg_risk < 10 else "⚠️ Review Required")
    summary_table.add_row(
        "High-Risk Accounts", str(len(high_risk_accounts)), "🔴 Immediate Action" if high_risk_accounts else "✅ Good"
    )
    summary_table.add_row(
        "Total Untagged Resources", str(total_untagged), "📋 Tag Management" if total_untagged > 50 else "✅ Good"
    )
    summary_table.add_row(
        "Total Unused EIPs", str(total_unused_eips), "💰 Cost Optimization" if total_unused_eips > 5 else "✅ Good"
    )

    console.print(summary_table)


def _initialize_profiles(
    args: argparse.Namespace,
) -> Tuple[List[str], Optional[List[str]], Optional[int]]:
    """Initialize AWS profiles based on arguments."""
    available_profiles = get_aws_profiles()
    if not available_profiles:
        console.log("[bold red]No AWS profiles found. Please configure AWS CLI first.[/]")
        raise SystemExit(1)

    profiles_to_use = []
    if args.profiles:
        for profile in args.profiles:
            if profile in available_profiles:
                profiles_to_use.append(profile)
            else:
                console.log(f"[yellow]Warning: Profile '{profile}' not found in AWS configuration[/]")
        if not profiles_to_use:
            console.log("[bold red]None of the specified profiles were found in AWS configuration.[/]")
            raise SystemExit(1)
    elif args.all:
        profiles_to_use = available_profiles
    else:
        if "default" in available_profiles:
            profiles_to_use = ["default"]
        else:
            profiles_to_use = available_profiles
            console.log("[yellow]No default profile found. Using all available profiles.[/]")

    return profiles_to_use, args.regions, args.time_range


def _run_audit_report(profiles_to_use: List[str], args: argparse.Namespace) -> None:
    """Generate and export an audit report with PDCA continuous improvement."""
    console.print("[bold bright_cyan]🔍 PLAN: Preparing comprehensive audit report...[/]")

    # Display multi-profile configuration
    billing_profile = os.getenv("BILLING_PROFILE")
    mgmt_profile = os.getenv("MANAGEMENT_PROFILE")
    ops_profile = os.getenv("CENTRALISED_OPS_PROFILE")

    if any([billing_profile, mgmt_profile, ops_profile]):
        console.print("[dim cyan]Multi-profile configuration detected:[/]")
        if billing_profile:
            console.print(f"[dim cyan]  • Billing operations: {billing_profile}[/]")
        if mgmt_profile:
            console.print(f"[dim cyan]  • Management operations: {mgmt_profile}[/]")
        if ops_profile:
            console.print(f"[dim cyan]  • Operational tasks: {ops_profile}[/]")
        console.print()

    # Enhanced table with better visual hierarchy
    table = Table(
        Column("Profile", justify="center", style="bold magenta"),
        Column("Account ID", justify="center", style="dim"),
        Column("Untagged Resources", style="yellow"),
        Column("Stopped EC2 Instances", style="red"),
        Column("Unused Volumes", style="orange1"),
        Column("Unused EIPs", style="cyan"),
        Column("Budget Alerts", style="bright_red"),
        Column("Risk Score", justify="center", style="bold"),
        title="🎯 AWS FinOps Audit Report - PDCA Enhanced",
        show_lines=True,
        box=box.ROUNDED,
        style="bright_cyan",
        caption="🚀 PDCA Cycle: Plan → Do → Check → Act",
    )

    audit_data = []
    raw_audit_data = []
    pdca_metrics = []  # New: Track PDCA improvement metrics
    nl = "\n"
    comma_nl = ",\n"

    console.print("[bold green]⚙️ DO: Collecting audit data across profiles...[/]")

    # Create progress tracker for enhanced user experience
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Collecting audit data", total=len(profiles_to_use))

        for profile in profiles_to_use:
            progress.update(task, description=f"Processing profile: {profile}")

            # Use operational session for resource discovery
            ops_session = _create_operational_session(profile)
            # Use management session for account and governance operations
            mgmt_session = _create_management_session(profile)
            # Use billing session for cost and budget operations
            billing_session = _create_cost_session(profile)

            account_id = get_account_id(mgmt_session) or "Unknown"
            regions = args.regions or get_accessible_regions(ops_session)

            try:
                # Use operational session for resource discovery
                untagged = get_untagged_resources(ops_session, regions)
                anomalies = []
                for service, region_map in untagged.items():
                    if region_map:
                        service_block = f"[bright_yellow]{service}[/]:\n"
                        for region, ids in region_map.items():
                            if ids:
                                ids_block = "\n".join(f"[orange1]{res_id}[/]" for res_id in ids)
                                service_block += f"\n{region}:\n{ids_block}\n"
                        anomalies.append(service_block)
                if not any(region_map for region_map in untagged.values()):
                    anomalies = ["None"]
            except Exception as e:
                anomalies = [f"Error: {str(e)}"]

            # Use operational session for EC2 and resource operations
            stopped = get_stopped_instances(ops_session, regions)
            stopped_list = [f"{r}:\n[gold1]{nl.join(ids)}[/]" for r, ids in stopped.items()] or ["None"]

            unused_vols = get_unused_volumes(ops_session, regions)
            vols_list = [f"{r}:\n[dark_orange]{nl.join(ids)}[/]" for r, ids in unused_vols.items()] or ["None"]

            unused_eips = get_unused_eips(ops_session, regions)
            eips_list = [f"{r}:\n{comma_nl.join(ids)}" for r, ids in unused_eips.items()] or ["None"]

            # Use billing session for budget data
            budget_data = get_budgets(billing_session)
            alerts = []
            for b in budget_data:
                if b["actual"] > b["limit"]:
                    alerts.append(f"[red1]{b['name']}[/]: ${b['actual']:.2f} > ${b['limit']:.2f}")
            if not alerts:
                alerts = ["✅ No budgets exceeded"]

            # Calculate risk score for PDCA improvement tracking
            risk_score = _calculate_risk_score(untagged, stopped, unused_vols, unused_eips, budget_data)
            risk_display = _format_risk_score(risk_score)

            # Track PDCA metrics
            pdca_metrics.append(
                {
                    "profile": profile,
                    "account_id": account_id,
                    "risk_score": risk_score,
                    "untagged_count": sum(len(ids) for region_map in untagged.values() for ids in region_map.values()),
                    "stopped_count": sum(len(ids) for ids in stopped.values()),
                    "unused_volumes_count": sum(len(ids) for ids in unused_vols.values()),
                    "unused_eips_count": sum(len(ids) for ids in unused_eips.values()),
                    "budget_overruns": len([b for b in budget_data if b["actual"] > b["limit"]]),
                }
            )

            audit_data.append(
                {
                    "profile": profile,
                    "account_id": account_id,
                    "untagged_resources": clean_rich_tags("\n".join(anomalies)),
                    "stopped_instances": clean_rich_tags("\n".join(stopped_list)),
                    "unused_volumes": clean_rich_tags("\n".join(vols_list)),
                    "unused_eips": clean_rich_tags("\n".join(eips_list)),
                    "budget_alerts": clean_rich_tags("\n".join(alerts)),
                    "risk_score": risk_score,
                }
            )

            # Data for JSON which includes raw audit data
            raw_audit_data.append(
                {
                    "profile": profile,
                    "account_id": account_id,
                    "untagged_resources": untagged,
                    "stopped_instances": stopped,
                    "unused_volumes": unused_vols,
                    "unused_eips": unused_eips,
                    "budget_alerts": budget_data,
                }
            )

            table.add_row(
                f"[dark_magenta]{profile}[/]",
                account_id,
                "\n".join(anomalies),
                "\n".join(stopped_list),
                "\n".join(vols_list),
                "\n".join(eips_list),
                "\n".join(alerts),
                risk_display,
            )

            progress.advance(task)
    console.print(table)

    # CHECK phase: Display PDCA improvement metrics
    console.print("\n[bold yellow]📊 CHECK: PDCA Improvement Analysis[/]")
    _display_pdca_summary(pdca_metrics)

    console.print(
        "[bold bright_cyan]📝 Note: Dashboard scans EC2, RDS, Lambda, ELBv2 resources across all accessible regions.\n[/]"
    )

    # ACT phase: Export reports with PDCA enhancements
    if args.report_name:  # Ensure report_name is provided for any export
        if args.report_type:
            for report_type in args.report_type:
                if report_type == "csv":
                    csv_path = export_audit_report_to_csv(audit_data, args.report_name, args.dir)
                    if csv_path:
                        console.print(f"[bright_green]Successfully exported to CSV format: {csv_path}[/]")
                elif report_type == "json":
                    json_path = export_audit_report_to_json(raw_audit_data, args.report_name, args.dir)
                    if json_path:
                        console.print(f"[bright_green]Successfully exported to JSON format: {json_path}[/]")
                elif report_type == "pdf":
                    pdf_path = export_audit_report_to_pdf(audit_data, args.report_name, args.dir)
                    if pdf_path:
                        console.print(f"[bright_green]✅ Successfully exported to PDF format: {pdf_path}[/]")

        # Generate PDCA improvement report
        console.print("\n[bold cyan]🎯 ACT: Generating PDCA improvement recommendations...[/]")
        pdca_path = generate_pdca_improvement_report(pdca_metrics, args.report_name, args.dir)
        if pdca_path:
            console.print(f"[bright_green]🚀 PDCA improvement report saved: {pdca_path}[/]")


def _run_trend_analysis(profiles_to_use: List[str], args: argparse.Namespace) -> None:
    """Analyze and display cost trends with multi-profile support."""
    console.print("[bold bright_cyan]Analysing cost trends...[/]")

    # Display billing profile information
    billing_profile = os.getenv("BILLING_PROFILE")
    if billing_profile:
        console.print(f"[dim cyan]Using billing profile for cost data: {billing_profile}[/]")

    raw_trend_data = []

    # Enhanced progress tracking for trend analysis
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True,
    ) as progress:
        if args.combine:
            account_profiles = defaultdict(list)
            task1 = progress.add_task("Grouping profiles by account", total=len(profiles_to_use))

            for profile in profiles_to_use:
                try:
                    # Use management session to get account ID
                    session = _create_management_session(profile)
                    account_id = get_account_id(session)
                    if account_id:
                        account_profiles[account_id].append(profile)
                except Exception as e:
                    console.print(f"[red]Error checking account ID for profile {profile}: {str(e)}[/]")
                progress.advance(task1)

            task2 = progress.add_task("Fetching cost trends", total=len(account_profiles))
            for account_id, profiles in account_profiles.items():
                progress.update(task2, description=f"Fetching trends for account: {account_id}")
                try:
                    primary_profile = profiles[0]
                    # Use billing session for cost trend data
                    cost_session = _create_cost_session(primary_profile)
                    cost_data = get_trend(cost_session, args.tag)
                    trend_data = cost_data.get("monthly_costs")

                    if not trend_data:
                        console.print(f"[yellow]No trend data available for account {account_id}[/]")
                        continue

                    profile_list = ", ".join(profiles)
                    console.print(f"\n[bright_yellow]Account: {account_id} (Profiles: {profile_list})[/]")
                    raw_trend_data.append(cost_data)
                    create_trend_bars(trend_data)
                except Exception as e:
                    console.print(f"[red]Error getting trend for account {account_id}: {str(e)}[/]")
                progress.advance(task2)

        else:
            task3 = progress.add_task("Fetching individual trends", total=len(profiles_to_use))
            for profile in profiles_to_use:
                progress.update(task3, description=f"Processing profile: {profile}")
                try:
                    # Use billing session for cost data
                    cost_session = _create_cost_session(profile)
                    # Use management session for account ID
                    mgmt_session = _create_management_session(profile)

                    cost_data = get_trend(cost_session, args.tag)
                    trend_data = cost_data.get("monthly_costs")
                    account_id = get_account_id(mgmt_session) or cost_data.get("account_id", "Unknown")

                    if not trend_data:
                        console.print(f"[yellow]No trend data available for profile {profile}[/]")
                        continue

                    console.print(f"\n[bright_yellow]Account: {account_id} (Profile: {profile})[/]")
                    raw_trend_data.append(cost_data)
                    create_trend_bars(trend_data)
                except Exception as e:
                    console.print(f"[red]Error getting trend for profile {profile}: {str(e)}[/]")
                progress.advance(task3)

    if raw_trend_data and args.report_name and args.report_type:
        if "json" in args.report_type:
            json_path = export_trend_data_to_json(raw_trend_data, args.report_name, args.dir)
            if json_path:
                console.print(f"[bright_green]Successfully exported trend data to JSON format: {json_path}[/]")


def _get_display_table_period_info(profiles_to_use: List[str], time_range: Optional[int]) -> Tuple[str, str, str, str]:
    """Get period information for the display table using appropriate billing profile."""
    if profiles_to_use:
        try:
            # Use billing session for cost data period information
            sample_session = _create_cost_session(profiles_to_use[0])
            sample_cost_data = get_cost_data(sample_session, time_range)
            previous_period_name = sample_cost_data.get("previous_period_name", "Last Month Due")
            current_period_name = sample_cost_data.get("current_period_name", "Current Month Cost")
            previous_period_dates = (
                f"{sample_cost_data['previous_period_start']} to {sample_cost_data['previous_period_end']}"
            )
            current_period_dates = (
                f"{sample_cost_data['current_period_start']} to {sample_cost_data['current_period_end']}"
            )
            return (
                previous_period_name,
                current_period_name,
                previous_period_dates,
                current_period_dates,
            )
        except Exception:
            pass  # Fall through to default values
    return "Last Month Due", "Current Month Cost", "N/A", "N/A"


def create_display_table(
    previous_period_dates: str,
    current_period_dates: str,
    previous_period_name: str = "Last Month Due",
    current_period_name: str = "Current Month Cost",
) -> Table:
    """Create and configure the display table with dynamic column names."""
    return Table(
        Column("AWS Account Profile", justify="center", vertical="middle"),
        Column(
            f"{previous_period_name}\n({previous_period_dates})",
            justify="center",
            vertical="middle",
        ),
        Column(
            f"{current_period_name}\n({current_period_dates})",
            justify="center",
            vertical="middle",
        ),
        Column("Cost By Service", vertical="middle"),
        Column("Budget Status", vertical="middle"),
        Column("EC2 Instance Summary", justify="center", vertical="middle"),
        title="CloudOps Runbooks FinOps Platform",
        caption="Enterprise Multi-Account Cost Optimization",
        box=box.ASCII_DOUBLE_HEAD,
        show_lines=True,
        style="bright_cyan",
    )


def add_profile_to_table(table: Table, profile_data: ProfileData) -> None:
    """Add profile data to the display table."""
    if profile_data["success"]:
        percentage_change = profile_data.get("percent_change_in_total_cost")
        change_text = ""

        if percentage_change is not None:
            if percentage_change > 0:
                change_text = f"\n\n[bright_red]⬆ {percentage_change:.2f}%"
            elif percentage_change < 0:
                change_text = f"\n\n[bright_green]⬇ {abs(percentage_change):.2f}%"
            elif percentage_change == 0:
                change_text = "\n\n[bright_yellow]➡ 0.00%[/]"

        current_month_with_change = f"[bold red]${profile_data['current_month']:.2f}[/]{change_text}"

        table.add_row(
            f"[bright_magenta]Profile: {profile_data['profile']}\nAccount: {profile_data['account_id']}[/]",
            f"[bold red]${profile_data['last_month']:.2f}[/]",
            current_month_with_change,
            "[bright_green]" + "\n".join(profile_data["service_costs_formatted"]) + "[/]",
            "[bright_yellow]" + "\n\n".join(profile_data["budget_info"]) + "[/]",
            "\n".join(profile_data["ec2_summary_formatted"]),
        )
    else:
        table.add_row(
            f"[bright_magenta]{profile_data['profile']}[/]",
            "[red]Error[/]",
            "[red]Error[/]",
            f"[red]Failed to process profile: {profile_data['error']}[/]",
            "[red]N/A[/]",
            "[red]N/A[/]",
        )


def _generate_dashboard_data(
    profiles_to_use: List[str],
    user_regions: Optional[List[str]],
    time_range: Optional[int],
    args: argparse.Namespace,
    table: Table,
) -> List[ProfileData]:
    """Fetch, process, and prepare the main dashboard data with multi-profile support."""
    export_data: List[ProfileData] = []

    # Enhanced progress tracking with enterprise-grade progress indicators
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="bright_green", finished_style="bright_green"),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=False,  # Keep progress visible
    ) as progress:
        if args.combine:
            account_profiles = defaultdict(list)
            grouping_task = progress.add_task("Grouping profiles by account", total=len(profiles_to_use))

            for profile in profiles_to_use:
                progress.update(grouping_task, description=f"Checking account for profile: {profile}")
                try:
                    # Use management session for account identification
                    mgmt_session = _create_management_session(profile)
                    current_account_id = get_account_id(mgmt_session)
                    if current_account_id:
                        account_profiles[current_account_id].append(profile)
                    else:
                        console.log(f"[yellow]Could not determine account ID for profile {profile}[/]")
                except Exception as e:
                    console.log(f"[bold red]Error checking account ID for profile {profile}: {str(e)}[/]")
                progress.advance(grouping_task)

            # Process combined profiles with enhanced progress tracking
            processing_task = progress.add_task("Processing account data", total=len(account_profiles))
            for account_id_key, profiles_list in account_profiles.items():
                progress.update(processing_task, description=f"Processing account: {account_id_key}")

                if len(profiles_list) > 1:
                    profile_data = _process_combined_profiles_enhanced(
                        account_id_key, profiles_list, user_regions, time_range, args.tag
                    )
                else:
                    profile_data = _process_single_profile_enhanced(
                        profiles_list[0], user_regions, time_range, args.tag
                    )
                export_data.append(profile_data)
                add_profile_to_table(table, profile_data)
                progress.advance(processing_task)

        else:
            # Process individual profiles with enhanced progress tracking
            individual_task = progress.add_task("Processing individual profiles", total=len(profiles_to_use))
            for profile in profiles_to_use:
                progress.update(individual_task, description=f"Processing profile: {profile}")
                profile_data = _process_single_profile_enhanced(profile, user_regions, time_range, args.tag)
                export_data.append(profile_data)
                add_profile_to_table(table, profile_data)
                progress.advance(individual_task)

    return export_data


def _process_single_profile_enhanced(
    profile: str,
    user_regions: Optional[List[str]] = None,
    time_range: Optional[int] = None,
    tag: Optional[List[str]] = None,
) -> ProfileData:
    """
    Enhanced single profile processing with multi-profile session support.
    Uses appropriate sessions for different operations: billing, management, operational.
    """
    try:
        # Use billing session for cost data
        cost_session = _create_cost_session(profile)
        cost_data = get_cost_data(cost_session, time_range, tag)

        # Use operational session for EC2 and resource operations
        ops_session = _create_operational_session(profile)

        if user_regions:
            profile_regions = user_regions
        else:
            profile_regions = get_accessible_regions(ops_session)

        ec2_data = ec2_summary(ops_session, profile_regions)
        service_costs, service_cost_data = process_service_costs(cost_data)
        budget_info = format_budget_info(cost_data["budgets"])
        account_id = cost_data.get("account_id", "Unknown") or "Unknown"
        ec2_summary_text = format_ec2_summary(ec2_data)
        percent_change_in_total_cost = change_in_total_cost(cost_data["current_month"], cost_data["last_month"])

        return {
            "profile": profile,
            "account_id": account_id,
            "last_month": cost_data["last_month"],
            "current_month": cost_data["current_month"],
            "service_costs": service_cost_data,
            "service_costs_formatted": service_costs,
            "budget_info": budget_info,
            "ec2_summary": ec2_data,
            "ec2_summary_formatted": ec2_summary_text,
            "success": True,
            "error": None,
            "current_period_name": cost_data["current_period_name"],
            "previous_period_name": cost_data["previous_period_name"],
            "percent_change_in_total_cost": percent_change_in_total_cost,
        }

    except Exception as e:
        console.log(f"[red]Error processing profile {profile}: {str(e)}[/]")
        return {
            "profile": profile,
            "account_id": "Error",
            "last_month": 0,
            "current_month": 0,
            "service_costs": [],
            "service_costs_formatted": [f"Failed to process profile: {str(e)}"],
            "budget_info": ["N/A"],
            "ec2_summary": {"N/A": 0},
            "ec2_summary_formatted": ["Error"],
            "success": False,
            "error": str(e),
            "current_period_name": "Current month",
            "previous_period_name": "Last month",
            "percent_change_in_total_cost": None,
        }


def _process_combined_profiles_enhanced(
    account_id: str,
    profiles: List[str],
    user_regions: Optional[List[str]] = None,
    time_range: Optional[int] = None,
    tag: Optional[List[str]] = None,
) -> ProfileData:
    """
    Enhanced combined profile processing with multi-profile session support.
    Aggregates data from multiple profiles in the same AWS account.
    """
    try:
        primary_profile = profiles[0]

        # Use billing session for cost data aggregation
        primary_cost_session = _create_cost_session(primary_profile)
        # Use operational session for resource data
        primary_ops_session = _create_operational_session(primary_profile)

        # Get cost data using billing session
        account_cost_data = get_cost_data(primary_cost_session, time_range, tag)

        if user_regions:
            profile_regions = user_regions
        else:
            profile_regions = get_accessible_regions(primary_ops_session)

        # Aggregate EC2 data from all profiles using operational sessions
        combined_ec2_data = defaultdict(int)
        for profile in profiles:
            try:
                profile_ops_session = _create_operational_session(profile)
                profile_ec2_data = ec2_summary(profile_ops_session, profile_regions)
                for instance_type, count in profile_ec2_data.items():
                    combined_ec2_data[instance_type] += count
            except Exception as e:
                console.log(f"[yellow]Warning: Could not get EC2 data for profile {profile}: {str(e)}[/]")

        service_costs, service_cost_data = process_service_costs(account_cost_data)
        budget_info = format_budget_info(account_cost_data["budgets"])
        ec2_summary_text = format_ec2_summary(dict(combined_ec2_data))
        percent_change_in_total_cost = change_in_total_cost(
            account_cost_data["current_month"], account_cost_data["last_month"]
        )

        profile_list = ", ".join(profiles)
        console.log(f"[dim cyan]Combined {len(profiles)} profiles for account {account_id}: {profile_list}[/]")

        return {
            "profile": f"Combined ({profile_list})",
            "account_id": account_id,
            "last_month": account_cost_data["last_month"],
            "current_month": account_cost_data["current_month"],
            "service_costs": service_cost_data,
            "service_costs_formatted": service_costs,
            "budget_info": budget_info,
            "ec2_summary": dict(combined_ec2_data),
            "ec2_summary_formatted": ec2_summary_text,
            "success": True,
            "error": None,
            "current_period_name": account_cost_data["current_period_name"],
            "previous_period_name": account_cost_data["previous_period_name"],
            "percent_change_in_total_cost": percent_change_in_total_cost,
        }

    except Exception as e:
        console.log(f"[red]Error processing combined profiles for account {account_id}: {str(e)}[/]")
        profile_list = ", ".join(profiles)
        return {
            "profile": f"Combined ({profile_list})",
            "account_id": account_id,
            "last_month": 0,
            "current_month": 0,
            "service_costs": [],
            "service_costs_formatted": [f"Failed to process combined profiles: {str(e)}"],
            "budget_info": ["N/A"],
            "ec2_summary": {"N/A": 0},
            "ec2_summary_formatted": ["Error"],
            "success": False,
            "error": str(e),
            "current_period_name": "Current month",
            "previous_period_name": "Last month",
            "percent_change_in_total_cost": None,
        }


def _export_dashboard_reports(
    export_data: List[ProfileData],
    args: argparse.Namespace,
    previous_period_dates: str,
    current_period_dates: str,
) -> None:
    """Export dashboard data to specified formats."""
    if args.report_name and args.report_type:
        for report_type in args.report_type:
            if report_type == "csv":
                csv_path = export_to_csv(
                    export_data,
                    args.report_name,
                    args.dir,
                    previous_period_dates=previous_period_dates,
                    current_period_dates=current_period_dates,
                )
                if csv_path:
                    console.print(f"[bright_green]Successfully exported to CSV format: {csv_path}[/]")
            elif report_type == "json":
                json_path = export_to_json(export_data, args.report_name, args.dir)
                if json_path:
                    console.print(f"[bright_green]Successfully exported to JSON format: {json_path}[/]")
            elif report_type == "pdf":
                pdf_path = export_cost_dashboard_to_pdf(
                    export_data,
                    args.report_name,
                    args.dir,
                    previous_period_dates=previous_period_dates,
                    current_period_dates=current_period_dates,
                )
                if pdf_path:
                    console.print(f"[bright_green]Successfully exported to PDF format: {pdf_path}[/]")


def run_dashboard(args: argparse.Namespace) -> int:
    """Main function to run the CloudOps Runbooks FinOps Platform with multi-profile support."""
    with Status("[bright_cyan]Initialising...", spinner="aesthetic", speed=0.4):
        profiles_to_use, user_regions, time_range = _initialize_profiles(args)

    # Display multi-profile configuration at startup
    billing_profile = os.getenv("BILLING_PROFILE")
    mgmt_profile = os.getenv("MANAGEMENT_PROFILE")
    ops_profile = os.getenv("CENTRALISED_OPS_PROFILE")

    if any([billing_profile, mgmt_profile, ops_profile]):
        console.print("\n[bold bright_cyan]🔧 Multi-Profile Configuration Detected[/]")
        config_table = Table(
            title="Profile Configuration", show_header=True, header_style="bold cyan", box=box.SIMPLE, style="dim"
        )
        config_table.add_column("Operation Type", style="bold")
        config_table.add_column("Profile", style="bright_cyan")
        config_table.add_column("Purpose", style="dim")

        if billing_profile:
            config_table.add_row("💰 Billing", billing_profile, "Cost Explorer & Budget API access")
        if mgmt_profile:
            config_table.add_row("🏛️ Management", mgmt_profile, "Account ID & Organizations operations")
        if ops_profile:
            config_table.add_row("⚙️ Operational", ops_profile, "EC2, S3, and resource discovery")

        console.print(config_table)
        console.print("[dim]Fallback: Using profile-specific sessions when env vars not set[/]\n")

    if args.audit:
        _run_audit_report(profiles_to_use, args)
        return 0

    if args.trend:
        _run_trend_analysis(profiles_to_use, args)
        return 0

    with Status("[bright_cyan]Initialising dashboard...", spinner="aesthetic", speed=0.4):
        (
            previous_period_name,
            current_period_name,
            previous_period_dates,
            current_period_dates,
        ) = _get_display_table_period_info(profiles_to_use, time_range)

        table = create_display_table(
            previous_period_dates,
            current_period_dates,
            previous_period_name,
            current_period_name,
        )

    export_data = _generate_dashboard_data(profiles_to_use, user_regions, time_range, args, table)
    console.print(table)
    _export_dashboard_reports(export_data, args, previous_period_dates, current_period_dates)

    return 0


def _run_cost_trend_analysis(profiles: List[str], args: argparse.Namespace) -> Dict[str, Any]:
    """
    Run cost trend analysis across multiple accounts.

    Args:
        profiles: List of AWS profiles to analyze
        args: Command line arguments

    Returns:
        Dict containing cost trend analysis results
    """
    try:
        # Import the new dashboard module
        from runbooks.finops.finops_dashboard import FinOpsConfig, MultiAccountCostTrendAnalyzer

        # Create configuration
        config = FinOpsConfig()
        config.dry_run = not args.live_mode if hasattr(args, "live_mode") else True

        # Run cost trend analysis
        analyzer = MultiAccountCostTrendAnalyzer(config)
        results = analyzer.analyze_cost_trends()

        console.log(f"[green]✅ Cost trend analysis completed for {len(profiles)} profiles[/]")

        if results.get("status") == "completed":
            cost_data = results["cost_trends"]
            optimization = results["optimization_opportunities"]

            console.log(f"[cyan]📊 Analyzed {cost_data['total_accounts']} accounts[/]")
            console.log(f"[cyan]💰 Total monthly spend: ${cost_data['total_monthly_spend']:,.2f}[/]")
            console.log(f"[cyan]🎯 Potential savings: {optimization['savings_percentage']:.1f}%[/]")

        return results

    except Exception as e:
        console.log(f"[red]❌ Cost trend analysis failed: {e}[/]")
        return {"status": "error", "error": str(e)}


def _run_resource_heatmap_analysis(
    profiles: List[str], cost_data: Dict[str, Any], args: argparse.Namespace
) -> Dict[str, Any]:
    """
    Run resource utilization heatmap analysis.

    Args:
        profiles: List of AWS profiles to analyze
        cost_data: Cost analysis data from previous step
        args: Command line arguments

    Returns:
        Dict containing resource heatmap analysis results
    """
    try:
        # Import the new dashboard module
        from runbooks.finops.finops_dashboard import FinOpsConfig, ResourceUtilizationHeatmapAnalyzer

        # Create configuration
        config = FinOpsConfig()
        config.dry_run = not args.live_mode if hasattr(args, "live_mode") else True

        # Run heatmap analysis
        analyzer = ResourceUtilizationHeatmapAnalyzer(config, cost_data)
        results = analyzer.analyze_resource_utilization()

        console.log(f"[green]✅ Resource heatmap analysis completed[/]")

        if results.get("status") == "completed":
            heatmap_data = results["heatmap_data"]
            efficiency = results["efficiency_scoring"]

            console.log(f"[cyan]🔥 Analyzed {heatmap_data['total_resources']:,} resources[/]")
            console.log(f"[cyan]⚡ Average efficiency: {efficiency['average_efficiency_score']:.1f}%[/]")

        return results

    except Exception as e:
        console.log(f"[red]❌ Resource heatmap analysis failed: {e}[/]")
        return {"status": "error", "error": str(e)}


def _run_executive_dashboard(
    discovery_results: Dict[str, Any],
    cost_analysis: Dict[str, Any],
    audit_results: Dict[str, Any],
    args: argparse.Namespace,
) -> Dict[str, Any]:
    """
    Generate executive dashboard summary.

    Args:
        discovery_results: Account discovery results
        cost_analysis: Cost analysis results
        audit_results: Audit results
        args: Command line arguments

    Returns:
        Dict containing executive dashboard results
    """
    try:
        # Import the new dashboard module
        from runbooks.finops.finops_dashboard import EnterpriseExecutiveDashboard, FinOpsConfig

        # Create configuration
        config = FinOpsConfig()
        config.dry_run = not args.live_mode if hasattr(args, "live_mode") else True

        # Generate executive dashboard
        dashboard = EnterpriseExecutiveDashboard(config, discovery_results, cost_analysis, audit_results)
        results = dashboard.generate_executive_summary()

        console.log(f"[green]✅ Executive dashboard generated[/]")

        # Display key metrics
        if "financial_overview" in results:
            fin = results["financial_overview"]
            status_icon = "✅" if fin["target_achieved"] else "⚠️"
            console.log(f"[cyan]💰 Monthly spend: ${fin['current_monthly_spend']:,.2f}[/]")
            console.log(f"[cyan]🎯 Target status: {status_icon}[/]")

        return results

    except Exception as e:
        console.log(f"[red]❌ Executive dashboard generation failed: {e}[/]")
        return {"status": "error", "error": str(e)}


def run_complete_finops_workflow(profiles: List[str], args: argparse.Namespace) -> Dict[str, Any]:
    """
    Run the complete FinOps analysis workflow.

    Args:
        profiles: List of AWS profiles to analyze
        args: Command line arguments

    Returns:
        Dict containing complete analysis results
    """
    try:
        # Import the new dashboard module
        from runbooks.finops.finops_dashboard import FinOpsConfig, run_complete_finops_analysis

        console.log("[blue]🚀 Starting complete FinOps analysis workflow...[/]")

        # Create configuration from args
        config = FinOpsConfig()
        config.dry_run = not args.live_mode if hasattr(args, "live_mode") else True

        # Run complete analysis
        results = run_complete_finops_analysis(config)

        console.log("[green]✅ Complete FinOps workflow completed successfully[/]")

        # Display summary
        if results.get("workflow_status") == "completed":
            if "cost_analysis" in results and results["cost_analysis"].get("status") == "completed":
                cost_data = results["cost_analysis"]["cost_trends"]
                optimization = results["cost_analysis"]["optimization_opportunities"]

                console.log(f"[cyan]📊 Analyzed {cost_data['total_accounts']} accounts[/]")
                console.log(f"[cyan]💰 Monthly spend: ${cost_data['total_monthly_spend']:,.2f}[/]")
                console.log(f"[cyan]🎯 Potential savings: {optimization['savings_percentage']:.1f}%[/]")
                console.log(f"[cyan]💵 Annual impact: ${optimization['annual_savings_potential']:,.2f}[/]")

            if "export_status" in results:
                successful = len(results["export_status"]["successful_exports"])
                failed = len(results["export_status"]["failed_exports"])
                console.log(f"[cyan]📄 Exports: {successful} successful, {failed} failed[/]")

        return results

    except Exception as e:
        console.log(f"[red]❌ Complete FinOps workflow failed: {e}[/]")
        return {"status": "error", "error": str(e)}
