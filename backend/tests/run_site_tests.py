"""
Standalone site test runner — runs without pytest.
Prints a color-coded report of all 50+ sites.

Usage (from backend/):
    python tests/run_site_tests.py
    python tests/run_site_tests.py --category news
    python tests/run_site_tests.py --category tech,ecommerce
    python tests/run_site_tests.py --concurrency 5
"""
from __future__ import annotations
import sys
import asyncio
import argparse
import time
from dataclasses import dataclass, field

# Add backend/ to path when run directly
sys.path.insert(0, ".")

from app.services.fetcher import fetch_html
from app.services.ai_query_engine import run_query
from tests.test_scraper_suite import SITES, Site

# ── ANSI colors ───────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"


@dataclass
class TestResult:
    site: Site
    passed: bool
    count: int = 0
    ai_powered: bool = False
    fallback: bool = False
    pages: int = 1
    first_result: str = ""
    error: str = ""
    duration: float = 0.0


async def test_one(site: Site, sem: asyncio.Semaphore) -> TestResult:
    async with sem:
        start = time.time()
        try:
            html, _ = await fetch_html(site.url)
            result = await run_query(html, site.query, base_url=site.url)
            duration = time.time() - start
            count = result.get("count", 0)
            first = result["results"][0][:100].replace("\n", " ") if result["results"] else ""
            passed = count >= site.min_results
            return TestResult(
                site=site, passed=passed, count=count,
                ai_powered=result.get("ai_powered", False),
                fallback=result.get("fallback", False),
                pages=result.get("pages_fetched", 1),
                first_result=first,
                duration=duration,
            )
        except Exception as exc:
            return TestResult(
                site=site, passed=False,
                error=str(exc)[:120],
                duration=time.time() - start,
            )


def print_result(r: TestResult, i: int, total: int) -> None:
    status = f"{GREEN}✓ PASS{RESET}" if r.passed else (
             f"{YELLOW}⚠ SKIP{RESET}" if r.error else f"{RED}✗ FAIL{RESET}")

    ai_badge = f"{CYAN}✦ AI{RESET}" if r.ai_powered else f"{DIM}rule{RESET}"
    fallback  = f" {YELLOW}[fallback]{RESET}" if r.fallback else ""
    pages_note = f" {BLUE}{r.pages}p{RESET}" if r.pages > 1 else ""

    host = r.site.url.split("/")[2].replace("www.", "")
    cat  = f"{DIM}[{r.site.category}]{RESET}"

    print(f"  {i:>2}/{total} {status} {cat} {BOLD}{host}{RESET}")
    print(f"       Query : {r.site.query!r}")

    if r.error:
        print(f"       Error : {YELLOW}{r.error}{RESET}")
    else:
        print(f"       Result: {ai_badge}{fallback}{pages_note} | "
              f"{GREEN}{r.count}{RESET} items | {r.duration:.1f}s")
        if r.first_result:
            print(f"       First : {DIM}{r.first_result!r}{RESET}")
    print()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Run scraper site tests")
    parser.add_argument("--category", default="",
                        help="Comma-separated categories to run (default: all)")
    parser.add_argument("--concurrency", type=int, default=3,
                        help="Max parallel requests (default: 3)")
    args = parser.parse_args()

    sites = SITES
    if args.category:
        cats = {c.strip() for c in args.category.split(",")}
        sites = [s for s in SITES if s.category in cats]

    total = len(sites)
    sem   = asyncio.Semaphore(args.concurrency)

    print(f"\n{BOLD}Web Scraper Toolkit — Site Test Suite{RESET}")
    print(f"Testing {total} sites | concurrency={args.concurrency}\n")
    print("─" * 60)

    tasks = [test_one(s, sem) for s in sites]
    results: list[TestResult] = []

    # Run and print as they complete
    i = 0
    for coro in asyncio.as_completed(tasks):
        r = await coro
        i += 1
        print_result(r, i, total)
        results.append(r)

    # ── Summary ───────────────────────────────────────────────────────────────
    passed  = sum(1 for r in results if r.passed)
    failed  = sum(1 for r in results if not r.passed and not r.error)
    skipped = sum(1 for r in results if r.error)
    ai_used = sum(1 for r in results if r.ai_powered)
    avg_t   = sum(r.duration for r in results) / len(results) if results else 0

    print("─" * 60)
    print(f"\n{BOLD}Results{RESET}")
    print(f"  {GREEN}✓ Passed : {passed}/{total}{RESET}")
    if failed:
        print(f"  {RED}✗ Failed : {failed}{RESET}")
    if skipped:
        print(f"  {YELLOW}⚠ Skipped: {skipped} (network/blocked){RESET}")
    print(f"  {CYAN}✦ AI used: {ai_used}/{total - skipped} queries{RESET}")
    print(f"  Avg time : {avg_t:.1f}s per site\n")

    # Categories breakdown
    from collections import defaultdict
    by_cat: dict[str, list[TestResult]] = defaultdict(list)
    for r in results:
        by_cat[r.site.category].append(r)

    print(f"{BOLD}By category{RESET}")
    for cat, cat_results in sorted(by_cat.items()):
        p = sum(1 for r in cat_results if r.passed)
        t = len(cat_results)
        bar = "█" * p + "░" * (t - p)
        print(f"  {cat:<15} {bar}  {p}/{t}")

    print()
    sys.exit(0 if passed == total - skipped else 1)


if __name__ == "__main__":
    asyncio.run(main())
