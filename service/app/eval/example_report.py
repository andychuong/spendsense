"""Example usage of report generation service."""

import logging
from sqlalchemy.orm import Session

from app.eval.report import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_report_generation(db_session: Session, output_dir: str = "./reports"):
    """Example of generating evaluation reports."""

    # Initialize report generator
    logger.info(f"Initializing report generator with output directory: {output_dir}")
    report_generator = ReportGenerator(db_session, output_dir=output_dir)

    # Generate individual reports
    logger.info("Generating individual reports...")

    # JSON metrics
    json_file = report_generator.generate_metrics_json()
    logger.info(f"Generated JSON metrics: {json_file}")

    # CSV metrics
    csv_file = report_generator.generate_metrics_csv()
    logger.info(f"Generated CSV metrics: {csv_file}")

    # Summary report
    summary_file = report_generator.generate_summary_report()
    logger.info(f"Generated summary report: {summary_file}")

    # Decision traces (combined JSON)
    traces_file = report_generator.generate_user_decision_traces(
        output_format="json",
        combined=True,
    )
    logger.info(f"Generated combined decision traces: {traces_file}")

    # Decision traces (per-user Markdown)
    traces_files = report_generator.generate_user_decision_traces(
        output_format="markdown",
        combined=False,
    )
    logger.info(f"Generated per-user decision traces: {traces_files}")

    # Generate all reports at once
    logger.info("Generating all reports at once...")
    all_reports = report_generator.generate_all_reports(
        include_json=True,
        include_csv=True,
        include_summary=True,
        include_traces=True,
        traces_format="json",
        traces_combined=True,
    )

    logger.info("Generated reports:")
    for report_type, filepath in all_reports.items():
        logger.info(f"  - {report_type}: {filepath}")

    return all_reports


if __name__ == "__main__":
    print("Example report generation service usage. Provide a database session to run.")
    print("\nUsage:")
    print("  from app.eval.report import ReportGenerator")
    print("  report_generator = ReportGenerator(db_session, output_dir='./reports')")
    print("  ")
    print("  # Generate individual reports")
    print("  json_file = report_generator.generate_metrics_json()")
    print("  csv_file = report_generator.generate_metrics_csv()")
    print("  summary_file = report_generator.generate_summary_report()")
    print("  traces_file = report_generator.generate_user_decision_traces(combined=True)")
    print("  ")
    print("  # Or generate all at once")
    print("  all_reports = report_generator.generate_all_reports()")



