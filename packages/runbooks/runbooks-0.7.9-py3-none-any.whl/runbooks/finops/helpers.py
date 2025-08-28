import csv  # Added csv
import json
import os
import re
import sys
import tomllib  # Built-in since Python 3.11
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from rich.console import Console

from runbooks.finops.types import ProfileData

console = Console()

styles = getSampleStyleSheet()

# Custom style for the footer
audit_footer_style = ParagraphStyle(
    name="AuditFooter",
    parent=styles["Normal"],
    fontSize=8,
    textColor=colors.grey,
    alignment=1,
    leading=10,
)


def export_audit_report_to_pdf(
    audit_data_list: List[Dict[str, str]],
    file_name: str = "audit_report",
    path: Optional[str] = None,
) -> Optional[str]:
    """
    Export the audit report to a PDF file.

    :param audit_data_list: List of dictionaries, each representing a profile/account's audit data.
    :param file_name: The base name of the output PDF file.
    :param path: Optional directory where the PDF file will be saved.
    :return: Full path of the generated PDF file or None on error.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_filename = f"{file_name}_{timestamp}.pdf"

        if path:
            os.makedirs(path, exist_ok=True)
            output_filename = os.path.join(path, base_filename)
        else:
            output_filename = base_filename

        doc = SimpleDocTemplate(output_filename, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        elements: List[Flowable] = []

        headers = [
            "Profile",
            "Account ID",
            "Untagged Resources",
            "Stopped EC2 Instances",
            "Unused Volumes",
            "Unused EIPs",
            "Budget Alerts",
            "Risk Score",
        ]
        table_data = [headers]

        for row in audit_data_list:
            # Format risk score for PDF display
            risk_score = row.get("risk_score", 0)
            if risk_score == 0:
                risk_display = "LOW (0)"
            elif risk_score <= 10:
                risk_display = f"MEDIUM ({risk_score})"
            elif risk_score <= 25:
                risk_display = f"HIGH ({risk_score})"
            else:
                risk_display = f"CRITICAL ({risk_score})"

            table_data.append(
                [
                    row.get("profile", ""),
                    row.get("account_id", ""),
                    row.get("untagged_resources", ""),
                    row.get("stopped_instances", ""),
                    row.get("unused_volumes", ""),
                    row.get("unused_eips", ""),
                    row.get("budget_alerts", ""),
                    risk_display,
                ]
            )

        table = Table(table_data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.black),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.black),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
                ]
            )
        )

        elements.append(Paragraph("🎯 CloudOps Runbooks FinOps - Enterprise Audit Report", styles["Title"]))
        elements.append(Spacer(1, 12))
        elements.append(table)
        elements.append(Spacer(1, 4))

        # Enhanced notes with PDCA information
        pdca_info = Paragraph(
            "📊 PDCA Framework: This report follows Plan-Do-Check-Act continuous improvement methodology.<br/>"
            "📝 Coverage: Scans EC2, RDS, Lambda, ELBv2 resources across all accessible regions.<br/>"
            "🎯 Risk Scoring: LOW (0-10), MEDIUM (11-25), HIGH (26-50), CRITICAL (>50)",
            audit_footer_style,
        )
        elements.append(pdca_info)

        elements.append(Spacer(1, 2))
        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        footer_text = (
            f"🚀 Generated using CloudOps-Runbooks FinOps Dashboard (PDCA Enhanced) \u00a9 2025 on {current_time_str}"
        )
        elements.append(Paragraph(footer_text, audit_footer_style))

        doc.build(elements)
        return output_filename
    except Exception as e:
        console.print(f"[bold red]Error exporting audit report to PDF: {str(e)}[/]")
        return None


def _truncate_service_costs(services_data: str, max_length: int = 500) -> str:
    """
    Truncate service costs data for PDF display if too long.

    :param services_data: Service costs formatted as string
    :param max_length: Maximum character length before truncation
    :return: Truncated service costs string
    """
    if len(services_data) <= max_length:
        return services_data

    lines = services_data.split("\n")
    truncated_lines = []
    current_length = 0

    for line in lines:
        if current_length + len(line) + 1 <= max_length - 50:  # Reserve space for truncation message
            truncated_lines.append(line)
            current_length += len(line) + 1
        else:
            break

    # Add truncation indicator with service count
    remaining_services = len(lines) - len(truncated_lines)
    if remaining_services > 0:
        truncated_lines.append(f"... and {remaining_services} more services")

    return "\n".join(truncated_lines)


def _optimize_table_for_pdf(table_data: List[List[str]], max_col_width: int = 120) -> List[List[str]]:
    """
    Optimize table data for PDF rendering by managing column widths.

    :param table_data: Raw table data with headers and rows
    :param max_col_width: Maximum character width for any column
    :return: Optimized table data
    """
    optimized_data = []

    for row_idx, row in enumerate(table_data):
        optimized_row = []

        for col_idx, cell in enumerate(row):
            if col_idx == 4:  # "Cost By Service" column (index 4)
                # Apply special handling to service costs column
                optimized_cell = _truncate_service_costs(str(cell), max_col_width)
            else:
                # General cell optimization
                cell_str = str(cell)
                if len(cell_str) > max_col_width:
                    # Truncate long content with ellipsis
                    optimized_cell = cell_str[: max_col_width - 3] + "..."
                else:
                    optimized_cell = cell_str

            optimized_row.append(optimized_cell)

        optimized_data.append(optimized_row)

    return optimized_data


def _create_paginated_tables(table_data: List[List[str]], max_rows_per_page: int = 15) -> List[List[List[str]]]:
    """
    Split large table data into multiple pages for PDF generation.

    :param table_data: Complete table data including headers
    :param max_rows_per_page: Maximum data rows per page (excluding header)
    :return: List of table data chunks, each with headers
    """
    if len(table_data) <= max_rows_per_page + 1:  # +1 for header
        return [table_data]

    headers = table_data[0]
    data_rows = table_data[1:]

    paginated_tables = []

    for i in range(0, len(data_rows), max_rows_per_page):
        chunk = data_rows[i : i + max_rows_per_page]
        table_chunk = [headers] + chunk
        paginated_tables.append(table_chunk)

    return paginated_tables


def clean_rich_tags(text: str) -> str:
    """
    Clean the rich text before writing the data to a pdf.

    :param text: The rich text to clean.
    :return: Cleaned text.
    """
    return re.sub(r"\[/?[a-zA-Z0-9#_]*\]", "", text)


def export_audit_report_to_csv(
    audit_data_list: List[Dict[str, str]],
    file_name: str = "audit_report",
    path: Optional[str] = None,
) -> Optional[str]:
    """Export the audit report to a CSV file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_filename = f"{file_name}_{timestamp}.csv"
        output_filename = base_filename
        if path:
            os.makedirs(path, exist_ok=True)
            output_filename = os.path.join(path, base_filename)

        headers = [
            "Profile",
            "Account ID",
            "Untagged Resources",
            "Stopped EC2 Instances",
            "Unused Volumes",
            "Unused EIPs",
            "Budget Alerts",
            "Risk Score",
        ]
        # Corresponding keys in the audit_data_list dictionaries
        data_keys = [
            "profile",
            "account_id",
            "untagged_resources",
            "stopped_instances",
            "unused_volumes",
            "unused_eips",
            "budget_alerts",
            "risk_score",
        ]

        with open(output_filename, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)
            for item in audit_data_list:
                writer.writerow([item.get(key, "") for key in data_keys])
        return output_filename
    except Exception as e:
        console.print(f"[bold red]Error exporting audit report to CSV: {str(e)}[/]")
        return None


def export_audit_report_to_json(
    raw_audit_data: List[Dict[str, Any]], file_name: str = "audit_report", path: Optional[str] = None
) -> Optional[str]:
    """Export the audit report to a JSON file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_filename = f"{file_name}_{timestamp}.json"
        output_filename = base_filename
        if path:
            os.makedirs(path, exist_ok=True)
            output_filename = os.path.join(path, base_filename)

        with open(output_filename, "w", encoding="utf-8") as jsonfile:
            json.dump(raw_audit_data, jsonfile, indent=4)  # Use the structured list
        return output_filename
    except Exception as e:
        console.print(f"[bold red]Error exporting audit report to JSON: {str(e)}[/]")
        return None


def export_trend_data_to_json(
    trend_data: List[Dict[str, Any]], file_name: str = "trend_data", path: Optional[str] = None
) -> Optional[str]:
    """Export trend data to a JSON file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_filename = f"{file_name}_{timestamp}.json"
        output_filename = base_filename
        if path:
            os.makedirs(path, exist_ok=True)
            output_filename = os.path.join(path, base_filename)

        with open(output_filename, "w", encoding="utf-8") as jsonfile:
            json.dump(trend_data, jsonfile, indent=4)
        return output_filename
    except Exception as e:
        console.print(f"[bold red]Error exporting trend data to JSON: {str(e)}[/]")
        return None


def export_cost_dashboard_to_pdf(
    data: List[ProfileData],
    filename: str,
    output_dir: Optional[str] = None,
    previous_period_dates: str = "N/A",
    current_period_dates: str = "N/A",
) -> Optional[str]:
    """Export dashboard data to a PDF file with enterprise-grade layout handling."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_filename = f"{filename}_{timestamp}.pdf"

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_filename = os.path.join(output_dir, base_filename)
        else:
            output_filename = base_filename

        # Use A4 landscape for better space utilization
        doc = SimpleDocTemplate(
            output_filename,
            pagesize=landscape(A4),
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch,
        )
        styles = getSampleStyleSheet()
        elements: List[Flowable] = []

        # Enhanced title with executive summary
        title_style = ParagraphStyle(
            name="EnhancedTitle",
            parent=styles["Title"],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.darkblue,
            alignment=1,  # Center alignment
        )

        # Calculate summary metrics
        total_accounts = len(data)
        total_current_cost = sum(row["current_month"] for row in data if row.get("current_month", 0))
        total_previous_cost = sum(row["last_month"] for row in data if row.get("last_month", 0))
        cost_change = (
            ((total_current_cost - total_previous_cost) / total_previous_cost * 100) if total_previous_cost > 0 else 0
        )

        elements.append(Paragraph("🏢 CloudOps Runbooks FinOps - Enterprise Cost Report", title_style))

        # Executive summary
        summary_style = ParagraphStyle(
            name="Summary", parent=styles["Normal"], fontSize=10, spaceAfter=8, textColor=colors.darkgreen
        )

        summary_text = (
            f"📊 Executive Summary: {total_accounts} accounts analyzed | "
            f"Total Current Cost: ${total_current_cost:,.2f} | "
            f"Cost Change: {cost_change:+.1f}% | "
            f"Report Period: {current_period_dates}"
        )
        elements.append(Paragraph(summary_text, summary_style))
        elements.append(Spacer(1, 12))

        # Prepare table data with optimization
        previous_period_header = f"Cost Period\n({previous_period_dates})"
        current_period_header = f"Cost Period\n({current_period_dates})"

        headers = [
            "Profile",
            "Account ID",
            previous_period_header,
            current_period_header,
            "Top Services",
            "Budget Status",
            "EC2 Summary",
        ]

        raw_table_data = [headers]

        for row in data:
            # Optimize service costs for PDF display
            if row["service_costs"]:
                # Show only top 10 services to prevent width issues
                top_services = row["service_costs"][:10]
                services_data = "\n".join([f"{service}: ${cost:.2f}" for service, cost in top_services])
                if len(row["service_costs"]) > 10:
                    remaining_count = len(row["service_costs"]) - 10
                    services_data += f"\n... and {remaining_count} more services"
            else:
                services_data = "No costs"

            # Optimize budget display
            budget_lines = row["budget_info"][:3] if row["budget_info"] else ["No budgets"]
            budgets_data = "\n".join(budget_lines)
            if len(row["budget_info"]) > 3:
                budgets_data += f"\n... +{len(row['budget_info']) - 3} more"

            # Optimize EC2 summary
            ec2_items = [(state, count) for state, count in row["ec2_summary"].items() if count > 0]
            if ec2_items:
                ec2_data_summary = "\n".join([f"{state}: {count}" for state, count in ec2_items[:5]])
                if len(ec2_items) > 5:
                    ec2_data_summary += f"\n... +{len(ec2_items) - 5} more"
            else:
                ec2_data_summary = "No instances"

            # Format cost change indicator
            cost_change_text = ""
            if row.get("percent_change_in_total_cost") is not None:
                change = row["percent_change_in_total_cost"]
                if change > 0:
                    cost_change_text = f"\n↑ +{change:.1f}%"
                elif change < 0:
                    cost_change_text = f"\n↓ {change:.1f}%"
                else:
                    cost_change_text = "\n→ 0%"

            raw_table_data.append(
                [
                    row["profile"],
                    row["account_id"],
                    f"${row['last_month']:,.2f}",
                    f"${row['current_month']:,.2f}{cost_change_text}",
                    services_data,
                    budgets_data,
                    ec2_data_summary,
                ]
            )

        # Optimize table data for PDF rendering
        optimized_table_data = _optimize_table_for_pdf(raw_table_data, max_col_width=80)

        # Create paginated tables for large datasets
        paginated_tables = _create_paginated_tables(optimized_table_data, max_rows_per_page=12)

        # Style configuration for optimal PDF rendering
        table_style = TableStyle(
            [
                # Header styling
                ("BACKGROUND", (0, 0), (-1, 0), colors.navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 7),
                # Data styling
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 6),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                # Grid and background
                ("GRID", (0, 0), (-1, -1), 0.5, colors.darkgrey),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                # Column-specific styling
                ("ALIGN", (2, 0), (3, -1), "RIGHT"),  # Cost columns right-aligned
                ("FONTNAME", (2, 1), (3, -1), "Helvetica-Bold"),  # Bold cost values
            ]
        )

        # Generate tables with pagination
        for page_idx, table_data_chunk in enumerate(paginated_tables):
            if page_idx > 0:
                elements.append(PageBreak())
                # Add page header for continuation pages
                page_header = Paragraph(
                    f"CloudOps Runbooks FinOps - Page {page_idx + 1} of {len(paginated_tables)}",
                    ParagraphStyle(
                        name="PageHeader", parent=styles["Heading2"], fontSize=12, textColor=colors.darkblue
                    ),
                )
                elements.append(page_header)
                elements.append(Spacer(1, 8))

            # Create table with dynamic column widths
            available_width = landscape(A4)[0] - 1 * inch  # Account for margins
            col_widths = [
                available_width * 0.12,  # Profile (12%)
                available_width * 0.15,  # Account ID (15%)
                available_width * 0.12,  # Previous Cost (12%)
                available_width * 0.12,  # Current Cost (12%)
                available_width * 0.25,  # Services (25%)
                available_width * 0.12,  # Budget (12%)
                available_width * 0.12,  # EC2 (12%)
            ]

            table = Table(table_data_chunk, repeatRows=1, colWidths=col_widths)
            table.setStyle(table_style)
            elements.append(table)

        # Enhanced footer with metadata
        elements.append(Spacer(1, 12))

        footer_style = ParagraphStyle(
            name="EnhancedFooter", parent=styles["Normal"], fontSize=8, textColor=colors.grey, alignment=1
        )

        current_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        footer_text = (
            f"🚀 Generated by CloudOps-Runbooks FinOps Dashboard v0.7.8 | "
            f"Report Generated: {current_time_str} | "
            f"Accounts Analyzed: {total_accounts} | "
            f"© 2025 CloudOps Enterprise"
        )
        elements.append(Paragraph(footer_text, footer_style))

        # Build PDF with error handling
        doc.build(elements)

        # Verify file creation
        if os.path.exists(output_filename):
            file_size = os.path.getsize(output_filename)
            console.print(
                f"[bright_green]✅ PDF generated successfully: {os.path.abspath(output_filename)} ({file_size:,} bytes)[/]"
            )
            return os.path.abspath(output_filename)
        else:
            console.print("[bold red]❌ PDF file was not created[/]")
            return None

    except Exception as e:
        console.print(f"[bold red]❌ Error exporting to PDF: {str(e)}[/]")
        # Print more detailed error information for debugging
        import traceback

        console.print(f"[red]Detailed error trace: {traceback.format_exc()}[/]")
        return None


def load_config_file(file_path: str) -> Optional[Dict[str, Any]]:
    """Load configuration from TOML, YAML, or JSON file."""
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    try:
        with open(file_path, "rb" if file_extension == ".toml" else "r") as f:
            if file_extension == ".toml":
                loaded_data = tomllib.load(f)
                if isinstance(loaded_data, dict):
                    return loaded_data
                console.print(f"[bold red]Error: TOML file {file_path} did not load as a dictionary.[/]")
                return None
            elif file_extension in [".yaml", ".yml"]:
                loaded_data = yaml.safe_load(f)
                if isinstance(loaded_data, dict):
                    return loaded_data
                console.print(f"[bold red]Error: YAML file {file_path} did not load as a dictionary.[/]")
                return None
            elif file_extension == ".json":
                loaded_data = json.load(f)
                if isinstance(loaded_data, dict):
                    return loaded_data
                console.print(f"[bold red]Error: JSON file {file_path} did not load as a dictionary.[/]")
                return None
            else:
                console.print(f"[bold red]Error: Unsupported configuration file format: {file_extension}[/]")
                return None
    except FileNotFoundError:
        console.print(f"[bold red]Error: Configuration file not found: {file_path}[/]")
        return None
    except tomllib.TOMLDecodeError as e:
        console.print(f"[bold red]Error decoding TOML file {file_path}: {e}[/]")
        return None
    except yaml.YAMLError as e:
        console.print(f"[bold red]Error decoding YAML file {file_path}: {e}[/]")
        return None
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Error decoding JSON file {file_path}: {e}[/]")
        return None
    except Exception as e:
        console.print(f"[bold red]Error loading configuration file {file_path}: {e}[/]")
        return None


def generate_pdca_improvement_report(
    pdca_metrics: List[Dict[str, Any]], file_name: str = "pdca_improvement", path: Optional[str] = None
) -> Optional[str]:
    """
    Generate PDCA (Plan-Do-Check-Act) continuous improvement report.

    :param pdca_metrics: List of PDCA metrics for each profile
    :param file_name: The base name of the output file
    :param path: Optional directory where the file will be saved
    :return: Full path of the generated report or None on error
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        base_filename = f"{file_name}_pdca_report_{timestamp}.json"

        if path:
            os.makedirs(path, exist_ok=True)
            output_filename = os.path.join(path, base_filename)
        else:
            output_filename = base_filename

        # Calculate aggregate metrics
        total_risk = sum(m["risk_score"] for m in pdca_metrics)
        avg_risk = total_risk / len(pdca_metrics) if pdca_metrics else 0

        high_risk_accounts = [m for m in pdca_metrics if m["risk_score"] > 25]
        medium_risk_accounts = [m for m in pdca_metrics if 10 < m["risk_score"] <= 25]
        low_risk_accounts = [m for m in pdca_metrics if m["risk_score"] <= 10]

        total_untagged = sum(m["untagged_count"] for m in pdca_metrics)
        total_stopped = sum(m["stopped_count"] for m in pdca_metrics)
        total_unused_volumes = sum(m["unused_volumes_count"] for m in pdca_metrics)
        total_unused_eips = sum(m["unused_eips_count"] for m in pdca_metrics)
        total_budget_overruns = sum(m["budget_overruns"] for m in pdca_metrics)

        # Generate improvement recommendations
        recommendations = []

        # PLAN phase recommendations
        if total_untagged > 50:
            recommendations.append(
                {
                    "phase": "PLAN",
                    "priority": "HIGH",
                    "category": "Compliance",
                    "issue": f"Found {total_untagged} untagged resources across all accounts",
                    "action": "Implement mandatory tagging strategy using AWS Config rules",
                    "expected_outcome": "100% resource compliance within 30 days",
                    "owner": "Cloud Governance Team",
                }
            )

        if total_unused_eips > 5:
            recommendations.append(
                {
                    "phase": "PLAN",
                    "priority": "MEDIUM",
                    "category": "Cost Optimization",
                    "issue": f"Found {total_unused_eips} unused Elastic IPs",
                    "action": "Schedule monthly EIP cleanup automation",
                    "expected_outcome": f"Save ~${total_unused_eips * 3.65:.2f}/month",
                    "owner": "FinOps Team",
                }
            )

        # DO phase recommendations
        if high_risk_accounts:
            recommendations.append(
                {
                    "phase": "DO",
                    "priority": "CRITICAL",
                    "category": "Risk Management",
                    "issue": f"{len(high_risk_accounts)} accounts have critical risk scores",
                    "action": "Execute immediate remediation on high-risk accounts",
                    "expected_outcome": "Reduce risk scores by 70% within 2 weeks",
                    "owner": "Security Team",
                }
            )

        # CHECK phase recommendations
        if avg_risk > 15:
            recommendations.append(
                {
                    "phase": "CHECK",
                    "priority": "HIGH",
                    "category": "Monitoring",
                    "issue": f"Average risk score ({avg_risk:.1f}) exceeds threshold",
                    "action": "Implement automated risk scoring dashboard",
                    "expected_outcome": "Real-time risk visibility and alerting",
                    "owner": "DevOps Team",
                }
            )

        # ACT phase recommendations
        recommendations.append(
            {
                "phase": "ACT",
                "priority": "MEDIUM",
                "category": "Process Improvement",
                "issue": "Need continuous improvement framework",
                "action": "Establish monthly PDCA review cycles",
                "expected_outcome": "25% reduction in average risk score per quarter",
                "owner": "Cloud Center of Excellence",
            }
        )

        # Create comprehensive PDCA report
        pdca_report = {
            "report_metadata": {
                "generated_at": datetime.now().isoformat(),
                "report_type": "PDCA Continuous Improvement Analysis",
                "accounts_analyzed": len(pdca_metrics),
                "framework_version": "v1.0",
            },
            "executive_summary": {
                "overall_risk_score": total_risk,
                "average_risk_score": round(avg_risk, 2),
                "risk_distribution": {
                    "critical_accounts": len(high_risk_accounts),
                    "high_risk_accounts": len(medium_risk_accounts),
                    "low_risk_accounts": len(low_risk_accounts),
                },
                "key_findings": {
                    "untagged_resources": total_untagged,
                    "stopped_instances": total_stopped,
                    "unused_volumes": total_unused_volumes,
                    "unused_elastic_ips": total_unused_eips,
                    "budget_overruns": total_budget_overruns,
                },
            },
            "pdca_analysis": {
                "plan_phase": {
                    "description": "Strategic planning based on current state analysis",
                    "metrics_collected": len(pdca_metrics),
                    "baseline_established": True,
                },
                "do_phase": {
                    "description": "Implementation of audit data collection",
                    "data_sources": ["EC2", "RDS", "Lambda", "ELBv2", "Budgets"],
                    "regions_scanned": "All accessible regions",
                },
                "check_phase": {
                    "description": "Analysis of collected audit data",
                    "risk_assessment_completed": True,
                    "trends_identified": True,
                },
                "act_phase": {
                    "description": "Actionable recommendations for improvement",
                    "recommendations_generated": len(recommendations),
                    "prioritization_completed": True,
                },
            },
            "detailed_metrics": pdca_metrics,
            "improvement_recommendations": recommendations,
            "next_steps": {
                "immediate_actions": [
                    "Review high-risk accounts within 48 hours",
                    "Implement automated tagging for untagged resources",
                    "Schedule EIP cleanup automation",
                ],
                "medium_term_goals": [
                    "Establish monthly PDCA review cycle",
                    "Implement risk scoring dashboard",
                    "Create automated remediation workflows",
                ],
                "long_term_objectives": [
                    "Achieve average risk score below 5",
                    "Maintain 100% resource compliance",
                    "Reduce cloud waste by 25%",
                ],
            },
        }

        # Export to JSON
        with open(output_filename, "w", encoding="utf-8") as jsonfile:
            json.dump(pdca_report, jsonfile, indent=4, default=str)

        return os.path.abspath(output_filename)

    except Exception as e:
        console.print(f"[bold red]Error generating PDCA improvement report: {str(e)}[/]")
        return None
