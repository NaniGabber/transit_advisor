import argparse
import csv
import random
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

ROUTES_COUNT = 50
STOPS_COUNT = 2000
TRIPS_COUNT = 500
STOP_TIMES_COUNT = 10000

BUILD_ID = int(datetime.now().timestamp())
random.seed(BUILD_ID)


def generate_feed(output_zip: Path) -> None:
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    temp_dir = output_zip.parent / "__gtfs_tmp__"
    temp_dir.mkdir(exist_ok=True)

    services = ["WKD", "SAT", "SUN"]
    route_types = [0, 2, 3]

    try:
        with open(
            temp_dir / "agency.txt",
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)

            writer.writerow(
                [
                    "agency_id",
                    "agency_name",
                    "agency_url",
                    "agency_timezone",
                ]
            )

            writer.writerow(
                [
                    "1",
                    "Transit Test Agency",
                    "https://example.com",
                    "Europe/Kyiv",
                ]
            )

        with open(
            temp_dir / "routes.txt",
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)

            writer.writerow(
                [
                    "route_id",
                    "agency_id",
                    "route_short_name",
                    "route_long_name",
                    "route_type",
                ]
            )

            for route_id in range(1, ROUTES_COUNT + 1):
                route_name = f"Route {route_id}"

                if random.random() < 0.05:
                    route_name += " Express"

                writer.writerow(
                    [
                        f"ROUTE_{route_id}",
                        "1",
                        route_id,
                        route_name,
                        random.choice(route_types),
                    ]
                )

        with open(
            temp_dir / "stops.txt",
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)

            writer.writerow(
                [
                    "stop_id",
                    "stop_name",
                    "stop_lat",
                    "stop_lon",
                ]
            )

            for stop_id in range(1, STOPS_COUNT + 1):
                writer.writerow(
                    [
                        f"STOP_{stop_id}",
                        f"Stop {stop_id}",
                        round(
                            49.0
                            + random.uniform(-1.5, 1.5)
                            + random.uniform(-0.002, 0.002),
                            6,
                        ),
                        round(
                            33.0
                            + random.uniform(-1.5, 1.5)
                            + random.uniform(-0.002, 0.002),
                            6,
                        ),
                    ]
                )

        with open(
            temp_dir / "trips.txt",
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)

            writer.writerow(
                [
                    "route_id",
                    "service_id",
                    "trip_id",
                ]
            )

            for trip_id in range(1, TRIPS_COUNT + 1):
                writer.writerow(
                    [
                        f"ROUTE_{random.randint(1, ROUTES_COUNT)}",
                        random.choice(services),
                        f"TRIP_{trip_id}",
                    ]
                )

        with open(
            temp_dir / "stop_times.txt",
            "w",
            newline="",
            encoding="utf-8",
        ) as f:
            writer = csv.writer(f)

            writer.writerow(
                [
                    "trip_id",
                    "arrival_time",
                    "departure_time",
                    "stop_id",
                    "stop_sequence",
                ]
            )

            generated = 0

            while generated < STOP_TIMES_COUNT:
                trip_id = random.randint(1, TRIPS_COUNT)

                stop_count = random.randint(5, 30)

                start_dt = datetime(
                    2026,
                    1,
                    1,
                    random.randint(4, 22),
                    random.randint(0, 59),
                    0,
                )

                start_dt += timedelta(
                    minutes=random.randint(-3, 3),
                )

                for seq in range(1, stop_count + 1):
                    if generated >= STOP_TIMES_COUNT:
                        break

                    travel_time = random.randint(2, 8)

                    if random.random() < 0.05:
                        travel_time += random.choice((-1, 1))

                    arrival = start_dt + timedelta(minutes=travel_time * seq)

                    departure = arrival + timedelta(seconds=random.randint(15, 120))

                    writer.writerow(
                        [
                            f"TRIP_{trip_id}",
                            arrival.strftime("%H:%M:%S"),
                            departure.strftime("%H:%M:%S"),
                            f"STOP_{random.randint(1, STOPS_COUNT)}",
                            seq,
                        ]
                    )

                    generated += 1

        with zipfile.ZipFile(
            output_zip,
            "w",
            compression=zipfile.ZIP_DEFLATED,
        ) as archive:
            for file_name in (
                "agency.txt",
                "routes.txt",
                "stops.txt",
                "trips.txt",
                "stop_times.txt",
            ):
                archive.write(
                    temp_dir / file_name,
                    arcname=file_name,
                )

        print(f"Created GTFS feed: {output_zip}")
        print(f"Build id: {BUILD_ID}")
        print(f"Routes: {ROUTES_COUNT}")
        print(f"Stops: {STOPS_COUNT}")
        print(f"Trips: {TRIPS_COUNT}")
        print(f"Stop Times: {STOP_TIMES_COUNT}")

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate test GTFS feed",
    )

    parser.add_argument(
        "output_zip",
        help="Output path, e.g. ./feeds/gtfs.zip",
    )

    args = parser.parse_args()

    output_zip = Path(args.output_zip)

    if output_zip.suffix.lower() != ".zip":
        raise SystemExit("Output file must have .zip extension")

    generate_feed(output_zip)


if __name__ == "__main__":
    main()
