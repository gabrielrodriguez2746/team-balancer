#!/usr/bin/env python3
"""
Fix sample size for complex constraints
"""

def fix_sample_size():
    """Increase sample size for complex constraints"""
    
    # Read the file
    with open('team_balancer.py', 'r') as f:
        content = f.read()
    
    # Replace the hardcoded sample size
    old_line = "            return self._generate_random_team_combinations(players, num_teams, team_size, n_samples=10000)"
    new_line = "            return self._generate_random_team_combinations(players, num_teams, team_size, n_samples=100000)"
    
    if old_line in content:
        content = content.replace(old_line, new_line)
        print("✅ Increased sample size from 10,000 to 100,000")
    else:
        print("❌ Could not find the sample size line")
        return False
    
    # Write the file back
    with open('team_balancer.py', 'w') as f:
        f.write(content)
    
    print("✅ Sample size fix applied successfully")
    return True

if __name__ == "__main__":
    fix_sample_size()
