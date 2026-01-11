"""
Real-time FinOps Dashboard - CLI Interface
Monitors reasoning_logs collection and displays agent activities
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from utils.mongo_client import FinOpsDB

# Load environment variables
load_dotenv()

console = Console()


def format_timestamp(timestamp):
    """Format ISO timestamp to readable format"""
    if not timestamp:
        return "N/A"
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            dt = timestamp
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(timestamp)[:19]


def calculate_total_savings(logs):
    """Calculate total potential savings from all approved decommissions"""
    total_savings = 0.0
    for log in logs:
        if log.get('workflow_status') == 'APPROVED' and log.get('recommendation') == 'DECOMMISSION':
            # Get hourly cost from context_data
            context_data = log.get('context_data', [])
            if context_data and len(context_data) > 0:
                hourly_cost = context_data[0].get('hourly_cost', 0)
                total_savings += hourly_cost
    
    return total_savings


def create_dashboard_table(logs):
    """Create the main dashboard table"""
    table = Table(
        title="[bold cyan]FinOps Agent Activity Log[/bold cyan]",
        show_header=True,
        header_style="bold magenta",
        border_style="blue",
        title_style="bold cyan"
    )
    
    table.add_column("Time", style="dim", width=19)
    table.add_column("Alert ID", style="cyan", width=15)
    table.add_column("Status", width=12)
    table.add_column("Recommendation", width=15)
    table.add_column("Confidence", justify="right", width=10)
    table.add_column("TX Hash", style="green", width=15)
    table.add_column("Amount", justify="right", width=12)
    
    for log in logs:
        # Format status with color
        status = log.get('workflow_status', 'UNKNOWN')
        if status == 'APPROVED':
            status_text = "[green]APPROVED[/green]"
        elif status == 'ESCALATED':
            status_text = "[yellow]ESCALATED[/yellow]"
        elif status == 'COMPLETED':
            status_text = "[blue]COMPLETED[/blue]"
        else:
            status_text = f"[dim]{status}[/dim]"
        
        # Format recommendation
        recommendation = log.get('recommendation', 'N/A')
        if recommendation == 'DECOMMISSION':
            rec_text = "[red]DECOMMISSION[/red]"
        elif recommendation == 'OPTIMIZE':
            rec_text = "[yellow]OPTIMIZE[/yellow]"
        elif recommendation == 'MONITOR':
            rec_text = "[cyan]MONITOR[/cyan]"
        else:
            rec_text = recommendation
        
        # Format confidence score
        confidence = log.get('confidence_score')
        if confidence:
            conf_text = f"{confidence:.4f}"
            if confidence >= 0.85:
                conf_text = f"[green]{conf_text}[/green]"
            else:
                conf_text = f"[yellow]{conf_text}[/yellow]"
        else:
            conf_text = "N/A"
        
        # Format transaction hash
        tx_hash = log.get('tx_hash', '')
        if tx_hash and tx_hash != 'N/A':
            tx_display = f"{tx_hash[:6]}...{tx_hash[-4:]}" if len(tx_hash) > 10 else tx_hash
        else:
            tx_display = "[dim]-[/dim]"
        
        # Format amount
        tx_amount = log.get('tx_amount')
        if tx_amount:
            amount_text = f"{tx_amount:.6f} ETH"
        else:
            amount_text = "[dim]-[/dim]"
        
        table.add_row(
            format_timestamp(log.get('created_at')),
            log.get('alert_id', 'N/A'),
            status_text,
            rec_text,
            conf_text,
            tx_display,
            amount_text
        )
    
    return table


def create_summary_panel(logs, refresh_time):
    """Create summary statistics panel"""
    total_logs = len(logs)
    approved = sum(1 for log in logs if log.get('workflow_status') == 'APPROVED')
    escalated = sum(1 for log in logs if log.get('workflow_status') == 'ESCALATED')
    total_savings = calculate_total_savings(logs)
    
    # Calculate total bounties paid
    total_bounties = sum(log.get('tx_amount', 0) for log in logs if log.get('tx_hash'))
    
    summary_text = Text()
    summary_text.append("FINOPS DASHBOARD SUMMARY\n\n", style="bold white")
    summary_text.append(f"Total Alerts Processed: ", style="white")
    summary_text.append(f"{total_logs}\n", style="bold cyan")
    summary_text.append(f"Approved: ", style="white")
    summary_text.append(f"{approved}", style="bold green")
    summary_text.append(f"  |  Escalated: ", style="white")
    summary_text.append(f"{escalated}\n", style="bold yellow")
    summary_text.append(f"\nPotential Savings: ", style="white")
    summary_text.append(f"${total_savings:.2f}/hr", style="bold green")
    summary_text.append(f" (${total_savings * 730:.2f}/month)\n", style="green")
    summary_text.append(f"Total Bounties Paid: ", style="white")
    summary_text.append(f"{total_bounties:.6f} ETH\n", style="bold magenta")
    summary_text.append(f"\nLast Refresh: ", style="dim")
    summary_text.append(f"{refresh_time}", style="dim cyan")
    
    return Panel(summary_text, border_style="green", title="[bold]Summary[/bold]")


def create_recent_activity_panel(logs):
    """Create panel showing most recent activity"""
    if not logs:
        return Panel("[dim]No recent activity[/dim]", title="[bold]Latest Activity[/bold]", border_style="blue")
    
    latest = logs[0]
    
    activity_text = Text()
    activity_text.append("Alert ID: ", style="white")
    activity_text.append(f"{latest.get('alert_id', 'N/A')}\n", style="bold cyan")
    activity_text.append("Status: ", style="white")
    
    status = latest.get('workflow_status', 'UNKNOWN')
    if status == 'APPROVED':
        activity_text.append(f"{status}\n", style="bold green")
    elif status == 'ESCALATED':
        activity_text.append(f"{status}\n", style="bold yellow")
    else:
        activity_text.append(f"{status}\n", style="bold blue")
    
    activity_text.append("Recommendation: ", style="white")
    activity_text.append(f"{latest.get('recommendation', 'N/A')}\n", style="bold magenta")
    
    # Show snippet of analysis
    analysis = latest.get('analysis', '')
    if analysis:
        snippet = analysis[:150] + "..." if len(analysis) > 150 else analysis
        activity_text.append("\nAnalysis: ", style="white")
        activity_text.append(f"{snippet}", style="dim")
    
    return Panel(activity_text, title="[bold]Latest Activity[/bold]", border_style="blue")


def generate_dashboard():
    """Generate the dashboard layout"""
    try:
        db = FinOpsDB()
        
        # Fetch recent reasoning logs (last 20)
        logs = list(db.reasoning_logs_collection.find().sort('created_at', -1).limit(20))
        
        db.close()
        
        # Create layout
        layout = Layout()
        
        # Split into header and body
        layout.split_column(
            Layout(name="header", size=10),
            Layout(name="body")
        )
        
        # Split header into summary and recent activity
        layout["header"].split_row(
            Layout(name="summary"),
            Layout(name="recent")
        )
        
        # Add content
        refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        layout["summary"].update(create_summary_panel(logs, refresh_time))
        layout["recent"].update(create_recent_activity_panel(logs))
        layout["body"].update(create_dashboard_table(logs))
        
        return layout
    
    except Exception as e:
        error_panel = Panel(
            f"[red]Error connecting to database:[/red]\n{str(e)}",
            title="[bold red]ERROR[/bold red]",
            border_style="red"
        )
        return Layout(error_panel)


def main():
    """Main dashboard loop"""
    console.clear()
    console.print("\n[bold cyan]Starting FinOps Real-Time Dashboard...[/bold cyan]")
    console.print("[dim]Press Ctrl+C to exit[/dim]\n")
    
    time.sleep(1)
    
    try:
        with Live(generate_dashboard(), refresh_per_second=0.5, console=console) as live:
            while True:
                time.sleep(2)  # Refresh every 2 seconds
                live.update(generate_dashboard())
    
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Dashboard stopped by user[/yellow]")
    except Exception as e:
        console.print(f"\n\n[red]Error:[/red] {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
