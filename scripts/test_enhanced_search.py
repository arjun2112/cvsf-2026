"""
Test Enhanced Semantic Search with Rich Table Output
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mongo_client import FinOpsDB
from dotenv import load_dotenv
from rich.console import Console

load_dotenv()
console = Console()

console.print("\n[bold cyan]═══════════════════════════════════════════════════════════════════════[/bold cyan]")
console.print("[bold cyan]Testing Enhanced Semantic Search with Strategic Clusters[/bold cyan]")
console.print("[bold cyan]═══════════════════════════════════════════════════════════════════════[/bold cyan]\n")

db = FinOpsDB()

# Test 1: Cost optimization query (should find high-value targets)
console.print("\n[bold yellow][SEARCH] Query 1: \"expensive resources to shut down for cost savings\"[/bold yellow]")
console.print("[dim]Expected: Should prioritize high-cost, low-priority targets (GPU cluster, oversized DB)[/dim]\n")
results = db.search_infra_context('expensive resources to shut down for cost savings', limit=5)
db.print_search_results(results)

# Test 2: Build infrastructure query (should find semantic variations)
console.print("\n\n[bold yellow][SEARCH] Query 2: \"continuous integration build servers\"[/bold yellow]")
console.print("[dim]Expected: Should find all 3 build runner variations despite different phrasing[/dim]\n")
results = db.search_infra_context('continuous integration build servers', limit=5)
db.print_search_results(results)

# Test 3: Red herring test - query should NOT dismiss junk-named servers
console.print("\n\n[bold yellow][SEARCH] Query 3: \"critical production failover systems\"[/bold yellow]")
console.print("[dim]Expected: Should include 'test-temp-01' despite name sounding like junk[/dim]\n")
results = db.search_infra_context('critical production failover systems', limit=5)
db.print_search_results(results)

# Test 4: Idle resources (should use diverse terminology)
console.print("\n\n[bold yellow][SEARCH] Query 4: \"dormant or zero-load infrastructure\"[/bold yellow]")
console.print("[dim]Expected: Should find idle/deprecated/abandoned resources using semantic understanding[/dim]\n")
results = db.search_infra_context('dormant or zero-load infrastructure', limit=5)
db.print_search_results(results)

# Test 5: Demo environment query (red herring test)
console.print("\n\n[bold yellow][SEARCH] Query 5: \"board presentation infrastructure\"[/bold yellow]")
console.print("[dim]Expected: Should find 'demo-sandbox-experimental' recognizing its importance[/dim]\n")
results = db.search_infra_context('board presentation infrastructure', limit=3)
db.print_search_results(results, show_content=True)

console.print("\n[bold green]═══════════════════════════════════════════════════════════════════════[/bold green]")
console.print("[bold green][OK] Enhanced semantic search testing completed![/bold green]")
console.print("[bold green]═══════════════════════════════════════════════════════════════════════[/bold green]\n")

db.close()
