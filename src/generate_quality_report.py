from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = (
    ROOT
    / "outputs"
    / "quality_reports"
)


def main():
    deliveries = pd.read_csv(
        REPORT_DIR / "delivery_status.csv"
    )

    issues = pd.read_csv(
        REPORT_DIR / "data_quality_issues.csv"
    )

    report_lines = [
        "# Automated Data Quality Report",
        "",
        "## Delivery summary",
        "",
        f"- Total deliveries: {len(deliveries)}",
        f"- Accepted: {(deliveries['status'] == 'ACCEPTED').sum()}",
        f"- Rejected for schema: {(deliveries['status'] == 'REJECTED_SCHEMA').sum()}",
        f"- Rejected for quality: {(deliveries['status'] == 'REJECTED_QUALITY').sum()}",
        "",
        "## Quality issues",
        "",
        f"- Total issues: {len(issues)}",
    ]

    if not issues.empty:
        error_count = (
            issues["severity"] == "ERROR"
        ).sum()

        warning_count = (
            issues["severity"] == "WARNING"
        ).sum()

        report_lines.extend(
            [
                f"- Errors: {error_count}",
                f"- Warnings: {warning_count}",
                "",
                "## Issues by rule",
                "",
            ]
        )

        rule_counts = (
            issues.groupby(
                ["rule_id", "severity"]
            )
            .size()
            .reset_index(name="count")
        )

        report_lines.append(
            rule_counts.to_markdown(
                index=False
            )
        )

    output_file = (
        REPORT_DIR
        / "quality_summary.md"
    )

    output_file.write_text(
        "\n".join(report_lines),
        encoding="utf-8"
    )

    print(
        f"Quality report created: "
        f"{output_file}"
    )


if __name__ == "__main__":
    main()