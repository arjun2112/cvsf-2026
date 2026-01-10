"""
Seed Infrastructure Knowledge Data - Enhanced Version
Generates diverse, strategically designed infrastructure documents
"""

import sys
import os
from datetime import datetime, UTC

# Add parent directory to path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mongo_client import FinOpsDB
from dotenv import load_dotenv


# Placeholder wallet address for all documents
DEVELOPER_WALLET = "0x8Bc3e7595f0bEb742d35Cc6634C0532925a3b844"


def generate_infrastructure_documents():
    """
    Generate 20 strategically designed infrastructure documents.
    
    Includes:
    - Red Herrings: High priority with deceptive names
    - High-Value Targets: Expensive but low priority
    - Semantic Variations: Different phrasings for similar resources
    - Diverse terminology and enriched descriptions
    
    Returns:
        List of infrastructure documents with enhanced metadata
    """
    documents = []
    
    # ========== RED HERRINGS (3) ==========
    # High priority but names sound like junk
    documents.extend([
        {
            "content": "The test-temp-01 server is a critical component of our production failover strategy. This dormant standby system automatically activates during primary datacenter outages, ensuring business continuity for our e-commerce platform serving 1M+ daily users. Despite its temporary-sounding name, this infrastructure was designated as the emergency failover node during Q4 2025 architecture review.",
            "metadata": {
                "name": "test-temp-01",
                "type": "compute",
                "environment": "production",
                "service": "failover-node",
                "region": "us-west-2",
                "instance_type": "m5.4xlarge"
            },
            "priority": "high",
            "owner_email": "infrastructure@company.com",
            "hourly_cost": 0.768,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "The demo-sandbox-experimental instance is the live environment powering our upcoming board demonstration scheduled for January 15th. This high-visibility showcase will demonstrate our new AI-driven analytics platform to potential Series B investors. The server hosts real-time data processing pipelines and must remain operational 24/7 leading up to the presentation. Zero downtime tolerance until demo completion.",
            "metadata": {
                "name": "demo-sandbox-experimental",
                "type": "compute",
                "environment": "demo",
                "service": "analytics-platform",
                "region": "us-east-1",
                "instance_type": "r5.2xlarge"
            },
            "priority": "high",
            "owner_email": "executive-demo@company.com",
            "hourly_cost": 0.504,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "The scratch-dev-prototype server functions as the primary development environment for our mission-critical payment processing refactor. This seemingly temporary infrastructure hosts the only working build of our PCI-DSS compliant payment gateway that launches next quarter. Contains proprietary fraud detection algorithms and integrated third-party payment processor connections. Development team depends on this for daily feature testing.",
            "metadata": {
                "name": "scratch-dev-prototype",
                "type": "compute",
                "environment": "development",
                "service": "payment-gateway",
                "region": "eu-west-1",
                "instance_type": "c5.xlarge"
            },
            "priority": "high",
            "owner_email": "payments-dev@company.com",
            "hourly_cost": 0.17,
            "developer_wallet": DEVELOPER_WALLET
        }
    ])
    
    # ========== HIGH-VALUE TARGETS (3) ==========
    # Expensive GPU/high-memory instances marked as low priority and safe to optimize
    documents.extend([
        {
            "content": "This deprecated ML training cluster was originally provisioned for an abandoned computer vision project from 2024. The infrastructure runs on expensive GPU-enabled instances but hasn't processed any training jobs in over 60 days. All model artifacts have been archived to S3 cold storage. The research team confirmed this environment is safe to decommission. Shutting down this zero-load infrastructure could yield substantial cost savings without impacting any active workflows.",
            "metadata": {
                "name": "Legacy GPU Training Cluster",
                "type": "compute",
                "environment": "development",
                "service": "ml-training",
                "region": "us-east-1",
                "instance_type": "p3.8xlarge"
            },
            "priority": "low",
            "owner_email": "ml-research-archive@company.com",
            "hourly_cost": 12.24,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "An oversized memory-optimized database instance that was right-sized incorrectly during initial provisioning. Current monitoring shows peak memory utilization at only 18%, indicating massive overprovisioning. The workload could easily run on a significantly smaller instance type. Database performance metrics confirm zero performance degradation risk from downsizing. This dormant capacity represents one of our highest-impact optimization opportunities.",
            "metadata": {
                "name": "Oversized Dev Database",
                "type": "database",
                "environment": "development",
                "service": "postgresql",
                "region": "us-west-2",
                "instance_type": "r5.16xlarge"
            },
            "priority": "low",
            "owner_email": "database-ops@company.com",
            "hourly_cost": 6.048,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "High-memory analytics node originally created for a one-time data migration project that completed in December 2025. The instance continues running despite project completion and has shown zero CPU activity for 45+ consecutive days. All migration scripts and data have been safely archived. Infrastructure team verified this dormant resource can be immediately terminated with no business impact. Represents significant unnecessary spend.",
            "metadata": {
                "name": "Data Migration Worker",
                "type": "analytics",
                "environment": "staging",
                "service": "spark",
                "region": "us-east-1",
                "instance_type": "r5.12xlarge"
            },
            "priority": "low",
            "owner_email": "data-platform-archive@company.com",
            "hourly_cost": 5.04,
            "developer_wallet": DEVELOPER_WALLET
        }
    ])
    
    # ========== SEMANTIC VARIATIONS - Build Runners (3) ==========
    # Same concept with different phrasing
    documents.extend([
        {
            "content": "Our primary CI/CD worker fleet handles automated build, test, and deployment pipelines for all microservices. These automation nodes process 500+ code commits daily, running comprehensive test suites and security scans. Each worker maintains isolated Docker environments for parallel job execution. The infrastructure auto-scales during peak development hours (9 AM - 6 PM PST) and scales down during off-hours to optimize costs while maintaining developer productivity.",
            "metadata": {
                "name": "CI/CD Worker Fleet",
                "type": "automation",
                "environment": "production",
                "service": "github-actions",
                "region": "us-west-2",
                "instance_type": "c5.2xlarge"
            },
            "priority": "medium",
            "owner_email": "devops@company.com",
            "hourly_cost": 0.34,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "The automation node cluster powers our continuous integration infrastructure, executing unit tests, integration tests, and code quality checks. These build servers support 12 engineering teams across frontend, backend, and mobile development. Each node runs Jenkins agents with pre-configured build tools and dependencies. Monitoring shows consistent utilization patterns with predictable peak hours, making this an excellent candidate for scheduled scaling policies.",
            "metadata": {
                "name": "Automation Node Cluster",
                "type": "automation",
                "environment": "production",
                "service": "jenkins",
                "region": "us-east-1",
                "instance_type": "c5.xlarge"
            },
            "priority": "medium",
            "owner_email": "build-systems@company.com",
            "hourly_cost": 0.17,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "Jenkins runner infrastructure dedicated to compiling, testing, and packaging our enterprise applications. These build agents handle multi-stage Docker builds, artifact generation, and deployment to various environments. The runner pool maintains warm standby capacity to ensure zero wait times for critical production deployments. Usage analytics indicate opportunity for right-sizing during weekend periods when development activity drops to minimal levels.",
            "metadata": {
                "name": "Jenkins Runner Pool",
                "type": "automation",
                "environment": "production",
                "service": "jenkins-runners",
                "region": "eu-central-1",
                "instance_type": "c5.large"
            },
            "priority": "medium",
            "owner_email": "release-engineering@company.com",
            "hourly_cost": 0.085,
            "developer_wallet": DEVELOPER_WALLET
        }
    ])
    
    # ========== REMAINING DIVERSE INFRASTRUCTURE (11) ==========
    documents.extend([
        {
            "content": "Our production PostgreSQL database cluster handles mission-critical transactional workloads, processing 15K+ queries per second with sub-10ms latency requirements. This multi-AZ deployment ensures high availability with automated failover capabilities. The database stores customer records, order history, and real-time inventory data. Configured with continuous backups and point-in-time recovery. This infrastructure is absolutely critical for business operations and requires 24/7 monitoring.",
            "metadata": {
                "name": "Critical Production DB",
                "type": "database",
                "environment": "production",
                "service": "postgresql",
                "region": "us-east-1",
                "instance_type": "db.r6g.xlarge"
            },
            "priority": "critical",
            "owner_email": "dbadmin@company.com",
            "hourly_cost": 0.75,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "A neglected staging web server that has been sitting idle for 96+ consecutive hours with zero incoming HTTP requests. Monitoring dashboards show flatlined traffic metrics and zero-load CPU utilization. The staging environment was superseded by our new containerized testing infrastructure deployed last month. Development team confirmed all testing workflows have migrated to the new platform. This dormant server represents unnecessary ongoing expenses with no active consumers.",
            "metadata": {
                "name": "Idle Staging Webserver",
                "type": "compute",
                "environment": "staging",
                "service": "nginx",
                "region": "us-west-2",
                "instance_type": "t3.medium"
            },
            "priority": "low",
            "owner_email": "staging-team@company.com",
            "hourly_cost": 0.042,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "Experimental sandbox for machine learning model development and hyperparameter tuning experiments. This GPU-accelerated environment runs TensorFlow and PyTorch workloads for our data science team's research initiatives. The infrastructure is utilized intermittently during active research sprints but sits unused between projects. Implementing scheduled start/stop policies could reduce costs by 70% without impacting data science productivity, as the team typically works standard business hours.",
            "metadata": {
                "name": "Dev Sandbox",
                "type": "compute",
                "environment": "development",
                "service": "tensorflow",
                "region": "us-east-1",
                "instance_type": "g4dn.xlarge"
            },
            "priority": "low",
            "owner_email": "datascience@company.com",
            "hourly_cost": 0.526,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "Production-grade Redis cache cluster providing sub-millisecond data access for session management and real-time analytics. This multi-node deployment handles 75K operations per second with automated failover and data persistence. The cache layer reduces database load by 60% and is critical for maintaining application performance during peak traffic. Configured with eviction policies and memory optimization. Any disruption would immediately degrade user experience across all customer-facing applications.",
            "metadata": {
                "name": "Production Redis Cache",
                "type": "cache",
                "environment": "production",
                "service": "redis",
                "region": "us-east-1",
                "instance_type": "cache.r6g.large"
            },
            "priority": "critical",
            "owner_email": "platform@company.com",
            "hourly_cost": 0.302,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "API Gateway infrastructure supporting user acceptance testing for new feature releases. This managed service handles authentication, rate limiting, and request routing for UAT environments. Configured to support 150 concurrent connections during testing cycles. The gateway auto-scales based on demand patterns and includes request logging for debugging. Testing teams rely on this infrastructure during pre-production validation phases before customer-facing deployments.",
            "metadata": {
                "name": "UAT API Gateway",
                "type": "api",
                "environment": "uat",
                "service": "api-gateway",
                "region": "eu-west-1",
                "instance_type": "api-gw-standard"
            },
            "priority": "medium",
            "owner_email": "qa-team@company.com",
            "hourly_cost": 0.035,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "Enterprise Kubernetes orchestration platform running 200+ containerized microservices across 15 worker nodes. This production cluster handles authentication services, payment processing, order management, and customer-facing APIs. Configured with horizontal pod autoscaling, automated rolling updates, and comprehensive monitoring. The infrastructure processes millions of API requests daily and is absolutely mission-critical for business operations. Zero-downtime deployments and instant rollback capabilities are mandatory requirements.",
            "metadata": {
                "name": "Production K8s Cluster",
                "type": "container",
                "environment": "production",
                "service": "kubernetes",
                "region": "us-east-1",
                "instance_type": "c5.2xlarge"
            },
            "priority": "critical",
            "owner_email": "devops@company.com",
            "hourly_cost": 3.06,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "Global content delivery network with edge locations spanning 60+ cities worldwide. This CDN infrastructure serves static assets, images, videos, and API responses with 99.99% uptime SLA. Configured with intelligent caching policies and automatic cache invalidation. The network reduces origin server load by 85% and dramatically improves page load times for international users. Critical for delivering optimal user experience and maintaining competitive performance benchmarks.",
            "metadata": {
                "name": "Global CDN",
                "type": "cdn",
                "environment": "production",
                "service": "cloudfront",
                "region": "global",
                "instance_type": "cdn-standard"
            },
            "priority": "critical",
            "owner_email": "infrastructure@company.com",
            "hourly_cost": 0.15,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "Centralized log aggregation cluster ingesting 750GB daily from 150+ distributed microservices and infrastructure components. This analytics platform powers operational dashboards, security monitoring, and troubleshooting workflows. Configured with 30-day retention policies and automated archival to cost-optimized storage. The system enables rapid incident response and provides critical visibility into system health. Essential infrastructure for maintaining production service reliability and security posture.",
            "metadata": {
                "name": "Production Elasticsearch",
                "type": "analytics",
                "environment": "production",
                "service": "elasticsearch",
                "region": "us-east-1",
                "instance_type": "r5.xlarge.elasticsearch"
            },
            "priority": "high",
            "owner_email": "sre@company.com",
            "hourly_cost": 0.42,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "Application Load Balancer distributing incoming traffic across 20 backend application servers with intelligent health checking and automatic failover. This networking infrastructure handles SSL/TLS termination, reducing encryption overhead on application servers. Configured to handle 15K requests per second with sub-50ms routing latency. The load balancer is critical for achieving high availability and horizontal scalability. Any disruption would immediately impact customer access to all web services.",
            "metadata": {
                "name": "Production ALB",
                "type": "networking",
                "environment": "production",
                "service": "application-load-balancer",
                "region": "us-east-1",
                "instance_type": "alb-standard"
            },
            "priority": "critical",
            "owner_email": "network-ops@company.com",
            "hourly_cost": 0.025,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "Enterprise data warehouse running on Redshift with 6-node cluster configuration. This analytics platform processes nightly ETL pipelines, aggregating data from 50+ source systems. Powers 300+ business intelligence dashboards consumed by analysts, executives, and data scientists. The warehouse handles complex analytical queries with sub-second response times. Critical for data-driven decision making and strategic planning across the organization. Scheduled maintenance windows must be carefully coordinated.",
            "metadata": {
                "name": "Production Data Warehouse",
                "type": "analytics",
                "environment": "production",
                "service": "redshift",
                "region": "us-east-1",
                "instance_type": "dc2.large"
            },
            "priority": "high",
            "owner_email": "data-platform@company.com",
            "hourly_cost": 1.0,
            "developer_wallet": DEVELOPER_WALLET
        },
        {
            "content": "An obsolete Windows Server 2019 instance from a discontinued proof-of-concept initiative that concluded in Q2 2025. Infrastructure audit logs show zero login activity for 120+ days and no running application processes. The project stakeholders have confirmed all valuable data was migrated before project termination. This deprecated server continues accumulating costs despite having no active purpose. Scheduled for immediate decommissioning pending final security review and data sanitization.",
            "metadata": {
                "name": "Abandoned Prototype",
                "type": "compute",
                "environment": "development",
                "service": "windows-server",
                "region": "eu-central-1",
                "instance_type": "t3.large"
            },
            "priority": "low",
            "owner_email": "legacy-systems@company.com",
            "hourly_cost": 0.0832,
            "developer_wallet": DEVELOPER_WALLET
        }
    ])
    
    # Add timestamps to all documents
    current_time = datetime.now(UTC)
    for doc in documents:
        doc["created_at"] = current_time
        doc["updated_at"] = current_time
    
    return documents


def main():
    """Main function to seed infrastructure data."""
    load_dotenv()
    
    print("=" * 70)
    print("FinOps Infrastructure Knowledge Seeding - Enhanced Version")
    print("=" * 70)
    print()
    
    try:
        # Initialize database connection
        print("Connecting to MongoDB Atlas...")
        db = FinOpsDB()
        
        # Check current state
        stats = db.get_collection_stats()
        current_count = stats.get('document_count', 0)
        print(f"Current documents in collection: {current_count}")
        
        # Clear existing documents
        if current_count > 0:
            print(f"\n⚠ Clearing {current_count} existing documents to avoid duplicates...")
            result = db.infra_collection.delete_many({})
            print(f"✓ Deleted {result.deleted_count} documents")
        
        print()
        
        # Generate documents
        print("Generating 20 strategically designed infrastructure documents...")
        documents = generate_infrastructure_documents()
        
        # Display summary
        print(f"\n✓ Generated {len(documents)} documents")
        
        print("\n" + "-" * 70)
        print("STRATEGIC CLUSTERS:")
        print("-" * 70)
        print("🎭 Red Herrings (High Priority + Deceptive Names):")
        print("   - test-temp-01, demo-sandbox-experimental, scratch-dev-prototype")
        print("\n💰 High-Value Targets (Expensive + Low Priority):")
        print("   - Legacy GPU Training Cluster ($12.24/hr)")
        print("   - Oversized Dev Database ($6.05/hr)")
        print("   - Data Migration Worker ($5.04/hr)")
        print("\n🔄 Semantic Variations (Build Runners):")
        print("   - CI/CD Worker Fleet")
        print("   - Automation Node Cluster")
        print("   - Jenkins Runner Pool")
        print("-" * 70)
        
        print("\nBreakdown by priority:")
        priorities = {}
        for doc in documents:
            priority = doc['priority']
            priorities[priority] = priorities.get(priority, 0) + 1
        
        for priority, count in sorted(priorities.items()):
            print(f"  - {priority.capitalize()}: {count}")
        
        print("\nBreakdown by environment:")
        environments = {}
        for doc in documents:
            env = doc['metadata']['environment']
            environments[env] = environments.get(env, 0) + 1
        
        for env, count in sorted(environments.items()):
            print(f"  - {env.capitalize()}: {count}")
        
        total_hourly_cost = sum(doc['hourly_cost'] for doc in documents)
        print(f"\nTotal hourly cost: ${total_hourly_cost:.2f}/hour")
        print(f"Estimated monthly cost: ${total_hourly_cost * 730:.2f}/month")
        
        # Identify high-cost low-priority resources
        high_value_targets = [d for d in documents if d['hourly_cost'] > 5.0 and d['priority'] == 'low']
        if high_value_targets:
            total_savings = sum(d['hourly_cost'] for d in high_value_targets)
            print(f"\n💡 Potential savings from high-value targets: ${total_savings:.2f}/hr (${total_savings * 730:.2f}/month)")
        
        # Seed the database
        print("\n" + "-" * 70)
        inserted_count = db.seed_infra_knowledge(documents)
        print("-" * 70)
        
        # Verify
        print("\nVerifying insertion...")
        new_stats = db.get_collection_stats()
        final_count = new_stats.get('document_count', 0)
        print(f"Total documents in collection: {final_count}")
        
        print("\n" + "=" * 70)
        print("✓ Seeding completed successfully!")
        print("=" * 70)
        print(f"\nYour Atlas cluster now has {final_count} enhanced infrastructure documents.")
        print("Features:")
        print("  ✓ Strategic red herrings for testing agent intelligence")
        print("  ✓ High-value optimization targets")
        print("  ✓ Semantic variations for testing search quality")
        print("  ✓ Enriched descriptions with diverse terminology")
        print("  ✓ All metadata fields populated (including developer_wallet)")
        print("\nYou can now use search_infra_context() and print_search_results() to query!")
        
        # Close connection
        db.close()
        
    except Exception as e:
        print(f"\n✗ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
