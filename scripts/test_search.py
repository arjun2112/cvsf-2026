"""
Test Semantic Search on Infrastructure Knowledge
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.mongo_client import FinOpsDB
from dotenv import load_dotenv

load_dotenv()
db = FinOpsDB()

print('Testing semantic search...\n')
print('='*70)

# Test query 1: Cost optimization
print('\nQuery 1: "How to reduce cloud costs and save money?"')
print('-'*70)
results = db.search_infra_context('How to reduce cloud costs and save money?', limit=5)
for i, result in enumerate(results, 1):
    print(f'\n{i}. {result["metadata"]["name"]} (Score: {result["score"]:.4f})')
    print(f'   Priority: {result["priority"]} | Cost: ${result["hourly_cost"]}/hr')
    print(f'   Owner: {result["owner_email"]}')
    print(f'   Content: {result["content"][:120]}...')

# Test query 2: Production databases
print('\n\n' + '='*70)
print('\nQuery 2: "Critical production database servers"')
print('-'*70)
results = db.search_infra_context('Critical production database servers', limit=3)
for i, result in enumerate(results, 1):
    print(f'\n{i}. {result["metadata"]["name"]} (Score: {result["score"]:.4f})')
    print(f'   Priority: {result["priority"]} | Cost: ${result["hourly_cost"]}/hr')
    print(f'   Environment: {result["metadata"]["environment"]}')
    print(f'   Content: {result["content"][:120]}...')

# Test query 3: ML/GPU infrastructure
print('\n\n' + '='*70)
print('\nQuery 3: "GPU machine learning infrastructure"')
print('-'*70)
results = db.search_infra_context('GPU machine learning infrastructure', limit=3)
for i, result in enumerate(results, 1):
    print(f'\n{i}. {result["metadata"]["name"]} (Score: {result["score"]:.4f})')
    print(f'   Priority: {result["priority"]} | Cost: ${result["hourly_cost"]}/hr')
    print(f'   Instance: {result["metadata"]["instance_type"]}')
    print(f'   Content: {result["content"][:120]}...')

# Test query 4: Idle resources
print('\n\n' + '='*70)
print('\nQuery 4: "Unused or idle resources to shut down"')
print('-'*70)
results = db.search_infra_context('Unused or idle resources to shut down', limit=3)
for i, result in enumerate(results, 1):
    print(f'\n{i}. {result["metadata"]["name"]} (Score: {result["score"]:.4f})')
    print(f'   Priority: {result["priority"]} | Cost: ${result["hourly_cost"]}/hr')
    print(f'   Potential savings: ${result["hourly_cost"] * 730:.2f}/month')
    print(f'   Content: {result["content"][:120]}...')

print('\n\n' + '='*70)
print('Semantic search tests completed!')
print('='*70)

db.close()
