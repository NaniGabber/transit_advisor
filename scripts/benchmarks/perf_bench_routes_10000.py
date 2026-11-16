import statistics
import time

from fastapi.testclient import TestClient

from transit_advisor.main import app

client = TestClient(app)


def main() -> None:
    # Прогрів
    for _ in range(10):
        client.get("/api/v1/routes?q=11")

    iterations = 10000
    measurements: list[float] = []

    for _ in range(iterations):
        start = time.perf_counter()

        response = client.get("/api/v1/routes?q=11")

        elapsed = time.perf_counter() - start

        if response.status_code != 200:
            raise RuntimeError(f"Unexpected status code: {response.status_code}")

        measurements.append(elapsed)

    measurements.sort()

    avg = statistics.mean(measurements)
    median = statistics.median(measurements)
    minimum = min(measurements)
    maximum = max(measurements)

    p95 = measurements[int(len(measurements) * 0.95) - 1]
    p99 = measurements[int(len(measurements) * 0.99) - 1]

    print("\n=== Routes Search Performance ===")
    print(f"Requests: {iterations}")
    print(f"Average: {avg * 1000:.2f} ms")
    print(f"Median:  {median * 1000:.2f} ms")
    print(f"Min:     {minimum * 1000:.2f} ms")
    print(f"P95:     {p95 * 1000:.2f} ms")
    print(f"P99:     {p99 * 1000:.2f} ms")
    print(f"Max:     {maximum * 1000:.2f} ms")


if __name__ == "__main__":
    main()
