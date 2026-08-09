import subprocess
import sys


STEPS = [
    "src.generate_synthetic_data",
    "src.validate_schema",
    "src.process_deliveries",
    "src.build_database",
    "src.run_extraction",
    "src.generate_quality_report",
]


def main():
    print(
        "Starting healthcare "
        "data-management pipeline\n"
    )

    for step_number, module in enumerate(
        STEPS,
        start=1,
    ):
        print(
            f"[{step_number}/{len(STEPS)}] "
            f"Running {module}"
        )

        subprocess.run(
            [
                sys.executable,
                "-m",
                module,
            ],
            check=True,
        )

    print(
        "\nPipeline completed successfully."
    )


if __name__ == "__main__":
    main()