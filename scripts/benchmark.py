"""
scripts/benchmark.py

Benchmark the /classify/{task} endpoint using httpx.AsyncClient.
Measures latency and throughput, with configurable total requests and concurrency.
"""

import argparse
import asyncio
import time
import statistics

import httpx

async def _fetch(client: httpx.AsyncClient, url: str, payload: dict) -> float:
    """Send one POST and return the elapsed time in seconds."""
    start = time.perf_counter()
    resp = await client.post(url, json=payload)
    elapsed = time.perf_counter() - start
    # optionally check resp.status_code, resp.json(), etc.
    return elapsed

async def run_benchmark(url: str, payload: dict, total: int, concurrency: int):
    semaphore = asyncio.Semaphore(concurrency)
    latencies: list[float] = []

    async def bound_fetch():
        async with semaphore:
            t = await _fetch(client, url, payload)
            latencies.append(t)

    async with httpx.AsyncClient(timeout=None) as client:
        tasks = [asyncio.create_task(bound_fetch()) for _ in range(total)]
        await asyncio.gather(*tasks)

    # compute stats
    latencies_ms = [l * 1000 for l in latencies]  # convert to ms
    print(f"\nBenchmark results for {total} requests @ concurrency {concurrency}:")
    print(f"  Success:        {len(latencies)}/{total}")
    print(f"  Total time:     {sum(latencies):.2f}s")
    print(f"  Throughput:     {total / sum(latencies):.2f} req/s")
    print(f"  Latency (ms):")
    print(f"    min:          {min(latencies_ms):.2f}")
    print(f"    max:          {max(latencies_ms):.2f}")
    print(f"    avg:          {statistics.mean(latencies_ms):.2f}")
    print(f"    median:       {statistics.median(latencies_ms):.2f}")
    print(f"    90th pctile:  {statistics.quantiles(latencies_ms, n=100)[89]:.2f}")
    print(f"    99th pctile:  {statistics.quantiles(latencies_ms, n=100)[98]:.2f}")

def parse_args():
    parser = argparse.ArgumentParser(description="Benchmark the classify endpoint")
    parser.add_argument(
        "--url",
        type=str,
        default="http://localhost:8000/classify/sentiment",
        help="Full URL of the classify endpoint"
    )
    parser.add_argument(
        "--text",
        type=str,
        default="Benchmark test payload",
        help="Text payload to send in each request"
    )
    parser.add_argument(
        "--requests", "-n",
        type=int,
        default=100,
        help="Total number of requests to send"
    )
    parser.add_argument(
        "--concurrency", "-c",
        type=int,
        default=10,
        help="Number of concurrent in-flight requests"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    payload = {"text": args.text}
    start_time = time.perf_counter()
    asyncio.run(run_benchmark(args.url, payload, args.requests, args.concurrency))
    total_secs = time.perf_counter() - start_time
    print(f"\nOverall elapsed time: {total_secs:.2f}s")
