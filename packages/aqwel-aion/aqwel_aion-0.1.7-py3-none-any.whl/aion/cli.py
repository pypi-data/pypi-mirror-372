#!/usr/bin/env python3
"""
Aqwel-Aion v0.1.7 Command Line Interface Module
===============================================

Professional command-line interface for AI research project management.
Enhanced in v0.1.7 with Git integration and advanced project operations.

Features:
- Comprehensive CLI for all Aion library functions
- Git repository management and operations
- File and project management commands
- Interactive help system and documentation
- Professional command structure and organization
- Integration with all Aion modules and utilities

Author: Aksel Aghajanyan
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import subprocess  # Import subprocess module to run shell commands
import argparse  # Import argparse for CLI argument parsing
import sys  # Import sys for system operations
try:
    from . import git  # Import Git integration module
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

def run_command(command):
    """Run a shell command and return its output."""
    # Execute the command in the shell, capture output, and decode as text
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout.strip()  # Return the trimmed standard output of the command

def run_help():
    """Return the help message of the CLI."""
    from io import StringIO  # Import StringIO to capture print output as a string
    import sys  # Import sys to redirect stdout temporarily
    import argparse  # Import argparse for CLI argument parsing

    # Create the main argument parser with a description
    parser = argparse.ArgumentParser(description="Aion CLI")
    
    # Create subparsers for different CLI commands
    subparsers = parser.add_subparsers(dest="command")

    # Add 'chat' command parser with help description
    subparsers.add_parser("chat", help="Start Aion Chat CLI")

    # Add 'embed' command parser with help description
    subparsers.add_parser("embed", help="Embed a text/code file")

    # Add 'eval' command parser with arguments for predictions and answers files
    eval_parser = subparsers.add_parser("eval", help="Evaluate prediction accuracy")
    eval_parser.add_argument("preds", type=str, help="Predictions file")
    eval_parser.add_argument("answers", type=str, help="Answers file")

    # Add 'prompt' command parser with optional '--type' argument (system/user)
    prompt_parser = subparsers.add_parser("prompt", help="Show a prompt template")
    prompt_parser.add_argument("--type", choices=["system", "user"], default="user")

    # Add 'watch' command parser with required 'filepath' argument
    watch_parser = subparsers.add_parser("watch", help="Watch a file for changes and embed")
    watch_parser.add_argument("filepath", type=str, help="File to watch for changes")

    # Add Git command parsers
    git_parser = subparsers.add_parser("git", help="Git repository operations")
    git_subparsers = git_parser.add_subparsers(dest="git_command", help="Git commands")
    
    # Git status command
    git_status_parser = git_subparsers.add_parser("status", help="Show repository status")
    git_status_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    
    # Git log command
    git_log_parser = git_subparsers.add_parser("log", help="Show commit history")
    git_log_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    git_log_parser.add_argument("--limit", type=int, default=10, help="Maximum number of commits to show")
    
    # Git branches command
    git_branches_parser = git_subparsers.add_parser("branches", help="List all branches")
    git_branches_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    
    # Git diff command
    git_diff_parser = git_subparsers.add_parser("diff", help="Show diff output")
    git_diff_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    git_diff_parser.add_argument("--commit", help="Commit hash to diff against")

    # Redirect stdout to a StringIO object to capture the help output
    help_io = StringIO()
    sys.stdout = help_io  # Redirect stdout to StringIO buffer
    
    parser.print_help()  # Print the help message of the parser (goes to help_io)
    
    sys.stdout = sys.__stdout__  # Restore the original stdout

    # Return the captured help message as a string
    return help_io.getvalue()

# Git command functions
def git_status_command(repo_path="."):
    """Display Git repository status."""
    if not GIT_AVAILABLE:
        print("❌ Git integration not available. Install GitPython with: pip install gitpython")
        return
    
    status = git.get_git_status(repo_path)
    
    if "error" in status:
        print(f"❌ {status['error']}")
        return
    
    print(f"📁 Repository: {status['repo_path']}")
    print(f"🌿 Branch: {status['current_branch']}")
    print(f"✨ Working Directory: {'Clean' if status['working_dir_clean'] else 'Dirty'}")
    
    if status['staged_files']:
        print(f"📝 Staged Files ({len(status['staged_files'])}):")
        for file in status['staged_files']:
            print(f"   + {file}")
    
    if status['untracked_files']:
        print(f"❓ Untracked Files ({len(status['untracked_files'])}):")
        for file in status['untracked_files']:
            print(f"   ? {file}")

def git_log_command(repo_path=".", limit=10):
    """Display recent commit history."""
    if not GIT_AVAILABLE:
        print("❌ Git integration not available. Install GitPython with: pip install gitpython")
        return
    
    commits = git.get_recent_commits(repo_path, limit)
    
    if not commits or "error" in commits[0]:
        print("❌ No commits found or error occurred")
        return
    
    print(f"📜 Recent Commits (showing {len(commits)}):")
    print("-" * 80)
    
    for commit in commits:
        print(f"🔖 {commit['hash']} - {commit['message']}")
        print(f"   👤 {commit['author']} | 📅 {commit['date']} | 📁 {commit['files_changed']} files")
        print()

def git_branches_command(repo_path="."):
    """List all branches."""
    if not GIT_AVAILABLE:
        print("❌ Git integration not available. Install GitPython with: pip install gitpython")
        return
    
    branches = git.list_branches(repo_path)
    
    if not branches or "error" in branches[0]:
        print("❌ No branches found or error occurred")
        return
    
    print("🌿 Branches:")
    print("-" * 40)
    
    for branch in branches:
        active_marker = "⭐" if branch['is_active'] else "  "
        print(f"{active_marker} {branch['name']}")
        print(f"   📅 Last commit: {branch['last_commit']} ({branch['last_commit_date']})")
        print()

def git_diff_command(repo_path=".", commit_hash=None):
    """Show diff for a commit or working directory."""
    if not GIT_AVAILABLE:
        print("❌ Git integration not available. Install GitPython with: pip install gitpython")
        return
    
    if commit_hash:
        diff_output = git.GitManager(repo_path).get_diff(commit_hash)
    else:
        diff_output = git.GitManager(repo_path).get_diff()
    
    if diff_output:
        print("📊 Diff Output:")
        print("=" * 80)
        print(diff_output)
    else:
        print("✨ No changes to show")

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="LinkAI-Aion - Enhanced AI Utilities Library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  aion git status                    # Show repository status
  aion git log --limit 5            # Show last 5 commits
  aion git branches                 # List all branches
  aion git diff                     # Show working directory changes
  aion git diff --commit abc123     # Show diff for specific commit
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Add existing commands
    subparsers.add_parser("chat", help="Start Aion Chat CLI")
    subparsers.add_parser("embed", help="Embed a text/code file")
    
    eval_parser = subparsers.add_parser("eval", help="Evaluate prediction accuracy")
    eval_parser.add_argument("preds", type=str, help="Predictions file")
    eval_parser.add_argument("answers", type=str, help="Answers file")
    
    prompt_parser = subparsers.add_parser("prompt", help="Show a prompt template")
    prompt_parser.add_argument("--type", choices=["system", "user"], default="user")
    
    watch_parser = subparsers.add_parser("watch", help="Watch a file for changes and embed")
    watch_parser.add_argument("filepath", type=str, help="File to watch for changes")
    
    # Add Git subparser
    git_parser = subparsers.add_parser("git", help="Git repository operations")
    git_subparsers = git_parser.add_subparsers(dest="git_command", help="Git commands")
    
    # Git status command
    git_status_parser = git_subparsers.add_parser("status", help="Show repository status")
    git_status_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    git_status_parser.set_defaults(func=git_status_command)
    
    # Git log command
    git_log_parser = git_subparsers.add_parser("log", help="Show commit history")
    git_log_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    git_log_parser.add_argument("--limit", type=int, default=10, help="Maximum number of commits to show")
    git_log_parser.set_defaults(func=git_log_command)
    
    # Git branches command
    git_branches_parser = git_subparsers.add_parser("branches", help="List all branches")
    git_branches_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    git_branches_parser.set_defaults(func=git_branches_command)
    
    # Git diff command
    git_diff_parser = git_subparsers.add_parser("diff", help="Show diff output")
    git_diff_parser.add_argument("--path", default=".", help="Repository path (default: current directory)")
    git_diff_parser.add_argument("--commit", help="Commit hash to diff against")
    git_diff_parser.set_defaults(func=git_diff_command)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle Git commands
    if args.command == "git" and hasattr(args, 'git_command'):
        if args.git_command == "status":
            git_status_command(args.path)
        elif args.git_command == "log":
            git_log_command(args.path, args.limit)
        elif args.git_command == "branches":
            git_branches_command(args.path)
        elif args.git_command == "diff":
            git_diff_command(args.path, args.commit)
        else:
            git_parser.print_help()
    elif args.command == "git":
        git_parser.print_help()
    else:
        parser.print_help()