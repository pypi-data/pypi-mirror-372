#!/usr/bin/env python3
"""
GitHub Project Setup Script for AiiDA Fireball Plugin

This script helps you set up a complete GitHub repository for the AiiDA Fireball plugin
with all necessary files, documentation, and configuration.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

def run_command(command, cwd=None, check=True):
    """Run a shell command and return the result."""
    print(f"Running: {command}")
    result = subprocess.run(
        command, shell=True, cwd=cwd, capture_output=True, text=True, check=check
    )
    if result.stdout:
        print(result.stdout)
    if result.stderr and result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result

def copy_source_files(source_dir, target_dir):
    """Copy the plugin source files to the GitHub project."""
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    # Create src directory structure
    src_target = target_path / "src"
    src_target.mkdir(exist_ok=True)
    
    # Copy aiida_fireball module
    aiida_fireball_source = source_path / "src" / "aiida_fireball"
    aiida_fireball_target = src_target / "aiida_fireball"
    
    if aiida_fireball_source.exists():
        if aiida_fireball_target.exists():
            shutil.rmtree(aiida_fireball_target)
        shutil.copytree(aiida_fireball_source, aiida_fireball_target)
        print(f"✓ Copied source files from {aiida_fireball_source} to {aiida_fireball_target}")
    else:
        print(f"⚠️  Source directory not found: {aiida_fireball_source}")
    
    # Copy tests
    tests_source = source_path / "tests"
    tests_target = target_path / "tests"
    
    if tests_source.exists():
        if tests_target.exists():
            shutil.rmtree(tests_target)
        shutil.copytree(tests_source, tests_target)
        print(f"✓ Copied tests from {tests_source} to {tests_target}")
    
    # Copy docs if they exist
    docs_source = source_path / "docs"
    docs_target = target_path / "docs"
    
    if docs_source.exists():
        if docs_target.exists():
            shutil.rmtree(docs_target)
        shutil.copytree(docs_source, docs_target)
        print(f"✓ Copied docs from {docs_source} to {docs_target}")

def setup_git_repository(project_dir, github_username, repo_name):
    """Initialize git repository and add GitHub remote."""
    os.chdir(project_dir)
    
    # Initialize git if not already done
    if not os.path.exists(".git"):
        run_command("git init")
        run_command("git branch -M main")
    
    # Add all files
    run_command("git add .")
    
    # Initial commit
    run_command("git commit -m 'Initial commit: AiiDA Fireball plugin with transport calculations'")
    
    # Add GitHub remote
    if github_username and repo_name:
        github_url = f"git@github.com:{github_username}/{repo_name}.git"
        run_command(f"git remote add origin {github_url}", check=False)
        print(f"✓ Added GitHub remote: {github_url}")
        print(f"📝 Next steps:")
        print(f"   1. Create repository on GitHub: https://github.com/new")
        print(f"   2. Repository name: {repo_name}")
        print(f"   3. Make it private if desired")
        print(f"   4. Run: git push -u origin main")

def create_additional_files(project_dir):
    """Create additional project files."""
    project_path = Path(project_dir)
    
    # Create CHANGELOG.md
    changelog_content = """# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial release of AiiDA Fireball plugin
- Support for basic Fireball calculations
- Advanced transport calculations with optional files:
  - interaction.optional
  - eta.optional  
  - trans.optional
  - bias.optional
- Birch-Murnaghan equation of state workflow
- Comprehensive test suite
- Complete documentation with tutorials
- GitHub Actions CI/CD pipeline

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [1.0.0] - 2024-01-XX

### Added
- Initial stable release
"""
    
    with open(project_path / "CHANGELOG.md", "w") as f:
        f.write(changelog_content)
    
    # Create .gitignore
    gitignore_content = """# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# AiiDA specific
.aiida/

# Sphinx documentation
docs/_build/
docs/build/

# Jupyter Notebook
.ipynb_checkpoints

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Temporary files
*.tmp
*.temp
temp/
"""
    
    with open(project_path / ".gitignore", "w") as f:
        f.write(gitignore_content)
    
    # Create MANIFEST.in
    manifest_content = """include README.md
include LICENSE
include CHANGELOG.md
include pyproject.toml
recursive-include src/aiida_fireball *.py
recursive-include tests *.py
recursive-include docs *.rst *.md *.py
recursive-include examples *.py *.md
global-exclude *.pyc
global-exclude __pycache__
"""
    
    with open(project_path / "MANIFEST.in", "w") as f:
        f.write(manifest_content)
    
    print("✓ Created additional project files")

def main():
    """Main setup function."""
    print("🚀 AiiDA Fireball GitHub Project Setup")
    print("=" * 50)
    
    # Get user input
    current_dir = Path.cwd()
    source_dir = current_dir.parent  # Assumes we're in github-project subdirectory
    
    print(f"Current directory: {current_dir}")
    print(f"Source directory: {source_dir}")
    
    github_username = input("Enter your GitHub username (optional): ").strip()
    repo_name = input("Enter repository name [aiida-fireball]: ").strip() or "aiida-fireball"
    
    # Copy source files
    print("\n📁 Copying source files...")
    copy_source_files(source_dir, current_dir)
    
    # Create additional files
    print("\n📝 Creating additional project files...")
    create_additional_files(current_dir)
    
    # Setup git repository
    print("\n🌐 Setting up Git repository...")
    setup_git_repository(current_dir, github_username, repo_name)
    
    # Install development dependencies
    print("\n📦 Installing development dependencies...")
    run_command("pip install -e .[dev]", check=False)
    
    # Install pre-commit hooks
    print("\n🔧 Setting up pre-commit hooks...")
    run_command("pre-commit install", check=False)
    
    print("\n✅ Setup complete!")
    print("\n📋 Next steps:")
    print("1. Review and customize the generated files")
    print("2. Create a new repository on GitHub")
    print("3. Push your code: git push -u origin main")
    print("4. Set up ReadTheDocs for documentation")
    print("5. Configure GitHub Actions secrets for PyPI publishing")
    print("\n🎉 Your AiiDA Fireball plugin is ready for GitHub!")

if __name__ == "__main__":
    main()
