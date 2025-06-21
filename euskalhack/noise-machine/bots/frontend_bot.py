#!/usr/bin/env python3
"""
Frontend Bot - Legitimate Frontend Developer Bot
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


class FrontendBot:
    """Legitimate frontend developer bot that creates real frontend projects"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url.rstrip('/')
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.token = None
        
        # Frontend bot specific token (different from malicious bot)
        self.frontend_token = "4acff7c1c9d6c041c383f491db7ce4808461dde3"
        
        # Legitimate frontend project templates
        self.project_templates = {
            'react': {
                'name': 'react-dashboard',
                'description': 'Modern React dashboard with TypeScript',
                'files': self._get_react_files()
            },
            'vue': {
                'name': 'vue-portfolio',
                'description': 'Vue.js portfolio website',
                'files': self._get_vue_files()
            },
            'vanilla': {
                'name': 'js-components',
                'description': 'Vanilla JavaScript component library',
                'files': self._get_vanilla_files()
            }
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
                repo_url = f"http://{self.username}:{self.frontend_token}@{base_url_without_protocol}/{self.username}/{repo_name}.git"
                
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
    
    def _get_react_files(self):
        """Get React project files"""
        return {
            'package.json': '''{
  "name": "react-dashboard",
  "version": "1.0.0",
  "description": "Modern React dashboard with TypeScript",
  "main": "index.js",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "typescript": "^4.9.5"
  },
  "devDependencies": {
    "react-scripts": "5.0.1",
    "@types/react": "^18.0.27",
    "@types/react-dom": "^18.0.10"
  }
}''',
            'src/App.tsx': '''import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Header />
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;''',
            'src/components/Dashboard.tsx': '''import React, { useState, useEffect } from 'react';

interface DashboardData {
  users: number;
  sales: number;
  revenue: number;
}

const Dashboard: React.FC = () => {
  const [data, setData] = useState<DashboardData>({
    users: 0,
    sales: 0,
    revenue: 0
  });

  useEffect(() => {
    // Simulate API call
    setTimeout(() => {
      setData({
        users: 1234,
        sales: 567,
        revenue: 89012
      });
    }, 1000);
  }, []);

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="stats-grid">
        <div className="stat-card">
          <h3>Users</h3>
          <p>{data.users}</p>
        </div>
        <div className="stat-card">
          <h3>Sales</h3>
          <p>{data.sales}</p>
        </div>
        <div className="stat-card">
          <h3>Revenue</h3>
          <p>${data.revenue}</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;''',
            'src/components/Header.tsx': '''import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="container">
        <h1>React Dashboard</h1>
        <nav>
          <ul>
            <li><a href="/">Home</a></li>
            <li><a href="/about">About</a></li>
            <li><a href="/contact">Contact</a></li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;''',
            'src/App.css': '''.App {
  text-align: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  background-color: #282c34;
  padding: 20px;
  color: white;
  margin-bottom: 30px;
}

.header .container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header nav ul {
  display: flex;
  list-style: none;
  gap: 20px;
  margin: 0;
  padding: 0;
}

.header nav a {
  color: white;
  text-decoration: none;
}

.dashboard h1 {
  margin-bottom: 30px;
  color: #333;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.stat-card {
  background: #f5f5f5;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #666;
}

.stat-card p {
  font-size: 2em;
  font-weight: bold;
  margin: 0;
  color: #333;
}''',
            'README.md': '''# React Dashboard

A modern React dashboard built with TypeScript.

## Features

- React 18 with TypeScript
- React Router for navigation
- Responsive design
- Modern CSS Grid layout
- Component-based architecture

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

## Available Scripts

- `npm start` - Runs the app in development mode
- `npm test` - Launches the test runner
- `npm run build` - Builds the app for production
- `npm run eject` - Ejects from Create React App

## Project Structure

```
src/
  components/
    Dashboard.tsx
    Header.tsx
  App.tsx
  App.css
  index.tsx
```

## Technologies Used

- React 18
- TypeScript
- React Router
- CSS Grid
- Modern ES6+ features
'''
        }
    
    def _get_vue_files(self):
        """Get Vue.js project files"""
        return {
            'package.json': '''{
  "name": "vue-portfolio",
  "version": "1.0.0",
  "description": "Vue.js portfolio website",
  "main": "index.js",
  "scripts": {
    "serve": "vue-cli-service serve",
    "build": "vue-cli-service build",
    "lint": "vue-cli-service lint"
  },
  "dependencies": {
    "vue": "^3.2.45",
    "vue-router": "^4.1.6"
  },
  "devDependencies": {
    "@vue/cli-service": "^5.0.8",
    "@vue/compiler-sfc": "^3.2.45"
  }
}''',
            'src/App.vue': '''<template>
  <div id="app">
    <Header />
    <router-view />
    <Footer />
  </div>
</template>

<script>
import Header from './components/Header.vue'
import Footer from './components/Footer.vue'

export default {
  name: 'App',
  components: {
    Header,
    Footer
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Arial', sans-serif;
  line-height: 1.6;
  color: #333;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}
</style>''',
            'src/components/Header.vue': '''<template>
  <header class="header">
    <div class="container">
      <div class="logo">
        <h1>My Portfolio</h1>
      </div>
      <nav class="nav">
        <ul>
          <li><router-link to="/">Home</router-link></li>
          <li><router-link to="/about">About</router-link></li>
          <li><router-link to="/projects">Projects</router-link></li>
          <li><router-link to="/contact">Contact</router-link></li>
        </ul>
      </nav>
    </div>
  </header>
</template>

<script>
export default {
  name: 'Header'
}
</script>

<style scoped>
.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo h1 {
  font-size: 1.8rem;
  font-weight: bold;
}

.nav ul {
  display: flex;
  list-style: none;
  gap: 2rem;
}

.nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.3s;
}

.nav a:hover {
  opacity: 0.8;
}

.nav a.router-link-active {
  border-bottom: 2px solid white;
}
</style>''',
            'src/components/Footer.vue': '''<template>
  <footer class="footer">
    <div class="container">
      <p>&copy; 2024 My Portfolio. All rights reserved.</p>
      <div class="social-links">
        <a href="#" aria-label="GitHub">GitHub</a>
        <a href="#" aria-label="LinkedIn">LinkedIn</a>
        <a href="#" aria-label="Twitter">Twitter</a>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer'
}
</script>

<style scoped>
.footer {
  background-color: #2c3e50;
  color: white;
  padding: 2rem 0;
  margin-top: auto;
}

.container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.social-links {
  display: flex;
  gap: 1rem;
}

.social-links a {
  color: white;
  text-decoration: none;
  transition: opacity 0.3s;
}

.social-links a:hover {
  opacity: 0.8;
}
</style>''',
            'src/views/Home.vue': '''<template>
  <div class="home">
    <section class="hero">
      <div class="container">
        <h1>Welcome to My Portfolio</h1>
        <p>I'm a passionate frontend developer creating amazing web experiences</p>
        <button class="cta-button" @click="scrollToProjects">View My Work</button>
      </div>
    </section>
    
    <section class="skills">
      <div class="container">
        <h2>My Skills</h2>
        <div class="skills-grid">
          <div class="skill-card" v-for="skill in skills" :key="skill.name">
            <h3>{{ skill.name }}</h3>
            <div class="skill-bar">
              <div class="skill-progress" :style="{ width: skill.level + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Home',
  data() {
    return {
      skills: [
        { name: 'Vue.js', level: 90 },
        { name: 'React', level: 85 },
        { name: 'JavaScript', level: 95 },
        { name: 'TypeScript', level: 80 },
        { name: 'CSS/SCSS', level: 90 },
        { name: 'Node.js', level: 75 }
      ]
    }
  },
  methods: {
    scrollToProjects() {
      this.$router.push('/projects')
    }
  }
}
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 4rem 0;
  text-align: center;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
}

.cta-button {
  background: white;
  color: #667eea;
  padding: 1rem 2rem;
  border: none;
  border-radius: 5px;
  font-size: 1.1rem;
  font-weight: bold;
  cursor: pointer;
  transition: transform 0.3s;
}

.cta-button:hover {
  transform: translateY(-2px);
}

.skills {
  padding: 4rem 0;
}

.skills h2 {
  text-align: center;
  margin-bottom: 3rem;
  font-size: 2.5rem;
}

.skills-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.skill-card {
  background: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.skill-card h3 {
  margin-bottom: 1rem;
  color: #333;
}

.skill-bar {
  background: #e9ecef;
  height: 10px;
  border-radius: 5px;
  overflow: hidden;
}

.skill-progress {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  height: 100%;
  border-radius: 5px;
  transition: width 0.3s ease;
}
</style>''',
            'README.md': '''# Vue.js Portfolio

A modern portfolio website built with Vue.js 3.

## Features

- Vue 3 with Composition API
- Vue Router for navigation
- Responsive design
- Modern CSS with gradients
- Component-based architecture
- Smooth animations and transitions

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run serve
   ```

3. Open [http://localhost:8080](http://localhost:8080) to view it in the browser.

## Available Scripts

- `npm run serve` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm run lint` - Lints and fixes files

## Project Structure

```
src/
  components/
    Header.vue
    Footer.vue
  views/
    Home.vue
  App.vue
  main.js
  router.js
```

## Technologies Used

- Vue.js 3
- Vue Router 4
- Modern CSS with Flexbox and Grid
- ES6+ JavaScript features
'''
        }
    
    def _get_vanilla_files(self):
        """Get Vanilla JavaScript project files"""
        return {
            'package.json': '''{
  "name": "js-components",
  "version": "1.0.0",
  "description": "Vanilla JavaScript component library",
  "main": "index.js",
  "scripts": {
    "start": "http-server -p 8080",
    "build": "webpack --mode production",
    "dev": "webpack --mode development --watch"
  },
  "devDependencies": {
    "http-server": "^14.1.1",
    "webpack": "^5.75.0",
    "webpack-cli": "^5.0.1"
  }
}''',
            'index.html': '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JavaScript Component Library</title>
    <link rel="stylesheet" href="css/styles.css">
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>JS Component Library</h1>
            <nav>
                <ul>
                    <li><a href="#modal">Modal</a></li>
                    <li><a href="#tabs">Tabs</a></li>
                    <li><a href="#accordion">Accordion</a></li>
                    <li><a href="#carousel">Carousel</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main class="main">
        <div class="container">
            <section id="modal" class="section">
                <h2>Modal Component</h2>
                <button id="openModal" class="btn btn-primary">Open Modal</button>
                <div id="modal1" class="modal">
                    <div class="modal-content">
                        <span class="close">&times;</span>
                        <h3>Modal Title</h3>
                        <p>This is a modal dialog built with vanilla JavaScript.</p>
                    </div>
                </div>
            </section>

            <section id="tabs" class="section">
                <h2>Tabs Component</h2>
                <div class="tabs">
                    <div class="tab-buttons">
                        <button class="tab-button active" data-tab="tab1">Tab 1</button>
                        <button class="tab-button" data-tab="tab2">Tab 2</button>
                        <button class="tab-button" data-tab="tab3">Tab 3</button>
                    </div>
                    <div class="tab-content">
                        <div id="tab1" class="tab-pane active">
                            <h3>Tab 1 Content</h3>
                            <p>This is the content for tab 1.</p>
                        </div>
                        <div id="tab2" class="tab-pane">
                            <h3>Tab 2 Content</h3>
                            <p>This is the content for tab 2.</p>
                        </div>
                        <div id="tab3" class="tab-pane">
                            <h3>Tab 3 Content</h3>
                            <p>This is the content for tab 3.</p>
                        </div>
                    </div>
                </div>
            </section>

            <section id="accordion" class="section">
                <h2>Accordion Component</h2>
                <div class="accordion">
                    <div class="accordion-item">
                        <button class="accordion-header">Section 1</button>
                        <div class="accordion-content">
                            <p>Content for section 1 goes here.</p>
                        </div>
                    </div>
                    <div class="accordion-item">
                        <button class="accordion-header">Section 2</button>
                        <div class="accordion-content">
                            <p>Content for section 2 goes here.</p>
                        </div>
                    </div>
                    <div class="accordion-item">
                        <button class="accordion-header">Section 3</button>
                        <div class="accordion-content">
                            <p>Content for section 3 goes here.</p>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </main>

    <script src="js/components.js"></script>
    <script src="js/main.js"></script>
</body>
</html>''',
            'js/components.js': '''// Modal Component
class Modal {
    constructor(modalId) {
        this.modal = document.getElementById(modalId);
        this.closeBtn = this.modal.querySelector('.close');
        this.init();
    }

    init() {
        this.closeBtn.addEventListener('click', () => this.close());
        window.addEventListener('click', (e) => {
            if (e.target === this.modal) {
                this.close();
            }
        });
    }

    open() {
        this.modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    close() {
        this.modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Tabs Component
class Tabs {
    constructor(tabsContainer) {
        this.container = tabsContainer;
        this.tabButtons = this.container.querySelectorAll('.tab-button');
        this.tabPanes = this.container.querySelectorAll('.tab-pane');
        this.init();
    }

    init() {
        this.tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabId = e.target.dataset.tab;
                this.switchTab(tabId);
            });
        });
    }

    switchTab(tabId) {
        // Remove active class from all buttons and panes
        this.tabButtons.forEach(btn => btn.classList.remove('active'));
        this.tabPanes.forEach(pane => pane.classList.remove('active'));

        // Add active class to clicked button and corresponding pane
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
        document.getElementById(tabId).classList.add('active');
    }
}

// Accordion Component
class Accordion {
    constructor(accordionContainer) {
        this.container = accordionContainer;
        this.headers = this.container.querySelectorAll('.accordion-header');
        this.init();
    }

    init() {
        this.headers.forEach(header => {
            header.addEventListener('click', (e) => {
                const item = e.target.parentNode;
                const content = item.querySelector('.accordion-content');
                const isActive = item.classList.contains('active');

                // Close all items
                this.container.querySelectorAll('.accordion-item').forEach(item => {
                    item.classList.remove('active');
                    item.querySelector('.accordion-content').style.maxHeight = null;
                });

                // Open clicked item if it wasn't active
                if (!isActive) {
                    item.classList.add('active');
                    content.style.maxHeight = content.scrollHeight + 'px';
                }
            });
        });
    }
}

// Utility Functions
const utils = {
    // Smooth scroll to element
    scrollTo(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth' });
        }
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Generate random ID
    generateId() {
        return Math.random().toString(36).substr(2, 9);
    }
};

// Export for use in other files
window.Components = {
    Modal,
    Tabs,
    Accordion,
    utils
};''',
            'js/main.js': '''// Initialize components when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Modal
    const modal = new Components.Modal('modal1');
    const openModalBtn = document.getElementById('openModal');
    openModalBtn.addEventListener('click', () => modal.open());

    // Initialize Tabs
    const tabsContainer = document.querySelector('.tabs');
    new Components.Tabs(tabsContainer);

    // Initialize Accordion
    const accordionContainer = document.querySelector('.accordion');
    new Components.Accordion(accordionContainer);

    // Smooth scrolling for navigation links
    const navLinks = document.querySelectorAll('nav a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            Components.utils.scrollTo(targetId);
        });
    });

    // Add some interactive features
    addInteractiveFeatures();
});

function addInteractiveFeatures() {
    // Add hover effects to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Add loading states
    const loadingButtons = document.querySelectorAll('.btn-primary');
    loadingButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const originalText = this.textContent;
            this.textContent = 'Loading...';
            this.disabled = true;
            
            setTimeout(() => {
                this.textContent = originalText;
                this.disabled = false;
            }, 1000);
        });
    });
}''',
            'css/styles.css': '''/* Reset and Base Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

/* Header Styles */
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.header .container {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.header h1 {
    font-size: 1.8rem;
}

.header nav ul {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.header nav a {
    color: white;
    text-decoration: none;
    font-weight: 500;
    transition: opacity 0.3s;
}

.header nav a:hover {
    opacity: 0.8;
}

/* Main Content */
.main {
    padding: 2rem 0;
}

.section {
    margin-bottom: 4rem;
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.section h2 {
    margin-bottom: 1.5rem;
    color: #333;
    font-size: 2rem;
}

/* Button Styles */
.btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.3s ease;
}

.btn-primary {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}

.btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    z-index: 2000;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
}

.modal-content {
    background-color: white;
    margin: 10% auto;
    padding: 2rem;
    border-radius: 8px;
    width: 90%;
    max-width: 500px;
    position: relative;
    animation: modalSlideIn 0.3s ease;
}

@keyframes modalSlideIn {
    from { transform: translateY(-50px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}

.close {
    position: absolute;
    right: 1rem;
    top: 1rem;
    font-size: 2rem;
    cursor: pointer;
    color: #999;
}

.close:hover {
    color: #333;
}

/* Tabs Styles */
.tabs {
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
}

.tab-buttons {
    display: flex;
    background-color: #f8f9fa;
    border-bottom: 1px solid #ddd;
}

.tab-button {
    flex: 1;
    padding: 1rem;
    border: none;
    background: none;
    cursor: pointer;
    font-size: 1rem;
    transition: background-color 0.3s;
}

.tab-button:hover {
    background-color: #e9ecef;
}

.tab-button.active {
    background-color: white;
    border-bottom: 2px solid #667eea;
}

.tab-content {
    padding: 2rem;
}

.tab-pane {
    display: none;
}

.tab-pane.active {
    display: block;
}

/* Accordion Styles */
.accordion-item {
    border: 1px solid #ddd;
    border-radius: 5px;
    margin-bottom: 0.5rem;
    overflow: hidden;
}

.accordion-header {
    width: 100%;
    padding: 1rem;
    border: none;
    background-color: #f8f9fa;
    text-align: left;
    cursor: pointer;
    font-size: 1rem;
    font-weight: 500;
    transition: background-color 0.3s;
}

.accordion-header:hover {
    background-color: #e9ecef;
}

.accordion-item.active .accordion-header {
    background-color: #667eea;
    color: white;
}

.accordion-content {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
}

.accordion-content p {
    padding: 1rem;
    margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
    .header .container {
        flex-direction: column;
        gap: 1rem;
    }
    
    .header nav ul {
        gap: 1rem;
    }
    
    .tab-buttons {
        flex-direction: column;
    }
    
    .section {
        padding: 1rem;
    }
}''',
            'README.md': '''# JavaScript Component Library

A collection of reusable vanilla JavaScript components with no dependencies.

## Features

- **Modal Component** - Accessible modal dialogs
- **Tabs Component** - Interactive tab navigation
- **Accordion Component** - Collapsible content sections
- **Utility Functions** - Helper functions for common tasks
- **Responsive Design** - Works on all device sizes
- **No Dependencies** - Pure vanilla JavaScript

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm start
   ```

3. Open [http://localhost:8080](http://localhost:8080) to view it in the browser.

## Usage

### Modal
```javascript
const modal = new Components.Modal('myModal');
modal.open();
modal.close();
```

### Tabs
```javascript
const tabsContainer = document.querySelector('.tabs');
new Components.Tabs(tabsContainer);
```

### Accordion
```javascript
const accordionContainer = document.querySelector('.accordion');
new Components.Accordion(accordionContainer);
```

## Project Structure

```
js/
  components.js  # Main component library
  main.js       # Application initialization
css/
  styles.css    # Component styles
index.html      # Demo page
```

## Components

### Modal
- Keyboard accessible
- Click outside to close
- Smooth animations
- Customizable content

### Tabs
- Keyboard navigation
- Accessible ARIA attributes
- Smooth transitions
- Flexible content

### Accordion
- Single or multiple open sections
- Smooth expand/collapse
- Keyboard accessible
- Customizable styling

## Browser Support

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details
'''
        }
    
    def create_frontend_project(self, project_type: str = 'react'):
        """Create a legitimate frontend project"""
        if project_type not in self.project_templates:
            project_type = 'react'
        
        template = self.project_templates[project_type]
        repo_name = f"{template['name']}-{random.randint(100, 999)}"
        
        print(f"Creating {project_type.upper()} project: {repo_name}")
        
        # Create repository
        if not self.create_repository(repo_name, template['description']):
            print("Failed to create repository")
            return False
        
        self.wait(2)
        
        # Upload all project files
        print("Uploading project files...")
        files_uploaded = 0
        
        for file_path, content in template['files'].items():
            success = self.upload_file(repo_name, file_path, content, f"Add {file_path}")
            if success:
                files_uploaded += 1
                print(f"  ✓ {file_path}")
            else:
                print(f"  ✗ Failed to upload {file_path}")
            self.wait(1)
        
        # Create a helpful issue
        self.create_helpful_issue(repo_name, project_type)
        
        print(f"Frontend project created successfully!")
        print(f"Repository: {repo_name}")
        print(f"Files uploaded: {files_uploaded}/{len(template['files'])}")
        return True
    
    def create_helpful_issue(self, repo_name: str, project_type: str):
        """Create a helpful issue with setup instructions"""
        title = "🚀 Project Setup Instructions"
        
        if project_type == 'react':
            body = """## Getting Started with React

Welcome to your new React project! Here's how to get started:

### Prerequisites
- Node.js 14+ installed
- npm or yarn package manager

### Installation
```bash
npm install
# or
yarn install
```

### Development
```bash
npm start
# or
yarn start
```

### Building for Production
```bash
npm run build
# or
yarn build
```

### Next Steps
- [ ] Customize the components in `src/components/`
- [ ] Add your own styling in `src/App.css`
- [ ] Set up routing for additional pages
- [ ] Add tests for your components
- [ ] Configure deployment (Netlify, Vercel, etc.)

### Useful Resources
- [React Documentation](https://reactjs.org/docs)
- [TypeScript Handbook](https://www.typescriptlang.org/docs)
- [React Router](https://reactrouter.com)

Happy coding! 🎉"""
        
        elif project_type == 'vue':
            body = """## Getting Started with Vue.js

Welcome to your new Vue.js project! Here's how to get started:

### Prerequisites
- Node.js 14+ installed
- npm or yarn package manager

### Installation
```bash
npm install
# or
yarn install
```

### Development
```bash
npm run serve
# or
yarn serve
```

### Building for Production
```bash
npm run build
# or
yarn build
```

### Next Steps
- [ ] Customize components in `src/components/`
- [ ] Add new views in `src/views/`
- [ ] Set up Vuex for state management
- [ ] Add Vue Router for navigation
- [ ] Configure deployment

### Useful Resources
- [Vue.js Documentation](https://vuejs.org/guide)
- [Vue Router](https://router.vuejs.org)
- [Vuex](https://vuex.vuejs.org)

Happy coding! 🎉"""
        
        else:  # vanilla
            body = """## Getting Started with Vanilla JavaScript

Welcome to your new JavaScript component library! Here's how to get started:

### Prerequisites
- Node.js 14+ installed (for development server)
- Modern web browser

### Development
```bash
npm install
npm start
```

### Building for Production
```bash
npm run build
```

### Usage
Include the components in your HTML:
```html
<script src="js/components.js"></script>
<script src="js/main.js"></script>
```

### Next Steps
- [ ] Add more components to the library
- [ ] Write unit tests
- [ ] Add TypeScript support
- [ ] Create npm package
- [ ] Add documentation site

### Useful Resources
- [MDN Web Docs](https://developer.mozilla.org)
- [JavaScript.info](https://javascript.info)
- [Web Components](https://web.dev/custom-elements-v1)

Happy coding! 🎉"""
        
        success = self.create_issue(repo_name, title, body)
        if success:
            print("Setup instructions issue created")
        return success
    
    def run_frontend_campaign(self, project_type: str = None):
        """Run a campaign to create legitimate frontend projects"""
        print("Starting FRONTEND DEVELOPER campaign")
        print("Objective: Create legitimate, useful frontend projects")
        
        # Don't use the token for authentication, use username/password
        if not self.authenticate():
            print("Authentication failed - aborting campaign")
            return False
        
        # Choose random project type if not specified
        if not project_type:
            project_type = random.choice(['react', 'vue', 'vanilla'])
        
        print(f"Creating {project_type.upper()} project...")
        success = self.create_frontend_project(project_type)
        
        if success:
            print("FRONTEND campaign completed successfully")
            print("Created legitimate, useful frontend project")
        else:
            print("FRONTEND campaign failed")
        
        return success

    def create_simple_html_project(self):
        """Create a simple HTML project - just one repository with one HTML file"""
        repo_name = f"simple-website-{random.randint(100, 999)}"
        
        print(f"Creating simple HTML project: {repo_name}")
        
        # Create repository
        if not self.create_repository(repo_name, "Simple HTML website"):
            print("Failed to create repository")
            return False
        
        self.wait(2)
        
        # Create a simple HTML file
        html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Simple Website</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        p {
            line-height: 1.6;
            color: #666;
        }
        .highlight {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to My Simple Website</h1>
        <p>This is a simple HTML page created by frontend-bot.</p>
        
        <div class="highlight">
            <h2>About This Project</h2>
            <p>This website was generated automatically to demonstrate basic HTML and CSS capabilities.</p>
        </div>
        
        <p>Features of this page:</p>
        <ul>
            <li>Clean, responsive design</li>
            <li>Modern CSS styling</li>
            <li>Professional appearance</li>
            <li>Mobile-friendly layout</li>
        </ul>
        
        <p>Created with ❤️ by frontend-bot</p>
    </div>
</body>
</html>'''
        
        # Upload the HTML file
        print("Uploading index.html...")
        success = self.upload_file(repo_name, "index.html", html_content, "Add simple HTML page")
        
        if success:
            print(f"✅ Simple HTML project created successfully!")
            print(f"Repository: {repo_name}")
            print(f"🔗 View at: {self.base_url}/{self.username}/{repo_name}")
            return True
        else:
            print("❌ Failed to upload HTML file")
            return False


def main():
    print("Frontend Bot - Simple HTML Creator")
    print("Creates a simple HTML website")
    print("=" * 50)
    
    # Configuration from environment variables
    gitea_url = os.getenv('GITEA_URL', 'http://127.0.0.1:63708')
    username = os.getenv('BOT_USERNAME', 'frontend-bot')
    token = os.getenv('BOT_TOKEN', '4acff7c1c9d6c041c383f491db7ce4808461dde3')
    
    print(f"Target: {gitea_url}")
    print(f"Bot User: {username}")
    print("=" * 50)
    
    # Create and run bot
    bot = FrontendBot(gitea_url, username, 'botpass123')  # password still needed for constructor
    
    # Authenticate with token
    if not bot.authenticate(token):
        print("Authentication failed")
        print("Check credentials and Gitea connectivity")
        return
    
    # Create simple HTML project
    success = bot.create_simple_html_project()
    
    if success:
        print("=" * 50)
        print("✅ Simple HTML project created successfully!")
        print("Check Gitea instance for the created project")
    else:
        print("❌ Failed to create HTML project")
        print("Check logs for details")


if __name__ == "__main__":
    main() 