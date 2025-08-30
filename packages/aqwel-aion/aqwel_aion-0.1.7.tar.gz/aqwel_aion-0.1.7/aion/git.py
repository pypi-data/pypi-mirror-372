#!/usr/bin/env python3
"""
Aqwel-Aion v0.1.7 Git Integration Module
=========================================

NEW IN v0.1.7: Complete Git repository management and analysis capabilities.
Professional Git integration for AI research project management.

Features:
- Repository status and comprehensive information
- Commit history analysis and tracking
- Branch management and operations
- Diff viewing and file comparison
- Git operations through integrated CLI interface

Author: Aksel Aghajanyan
License: Apache-2.0
Copyright: 2025 Aqwel AI
"""

import os
from typing import List, Dict, Optional, Tuple

# Try to import GitPython, but make it optional
try:
    from git import Repo, GitCommandError
    from git.objects.commit import Commit
    from git.refs.remote import RemoteReference
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False
    # Create dummy classes for when GitPython is not available
    class Repo:
        pass
    class GitCommandError:
        pass
    class Commit:
        pass
    class RemoteReference:
        pass

class GitManager:
    """Manages Git repository operations and provides analysis tools."""
    
    def __init__(self, repo_path: str = None):
        """
        Initialize Git manager for a repository.
        
        Args:
            repo_path (str): Path to Git repository (defaults to current directory)
        """
        self.repo_path = repo_path or os.getcwd()
        self.repo = None
        self._initialize_repo()
    
    def _initialize_repo(self):
        """Initialize Git repository connection."""
        if not GIT_AVAILABLE:
            raise ValueError("GitPython is not available. Install with: pip install gitpython")
        
        try:
            self.repo = Repo(self.repo_path)
        except Exception as e:
            self.repo = None
            raise ValueError(f"Not a Git repository: {self.repo_path}")
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current repository status.
        
        Returns:
            Dict containing repository status information
        """
        if not self.repo:
            return {"error": "Not a Git repository"}
        
        try:
            # Get current branch
            current_branch = self.repo.active_branch.name
            
            # Get working directory status
            working_dir_clean = not self.repo.is_dirty()
            
            # Get staged changes
            staged_files = [item.a_path for item in self.repo.index.diff('HEAD')]
            
            # Get untracked files
            untracked_files = self.repo.untracked_files
            
            return {
                "current_branch": current_branch,
                "working_dir_clean": working_dir_clean,
                "staged_files": staged_files,
                "untracked_files": untracked_files,
                "repo_path": self.repo_path
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_commit_history(self, max_commits: int = 10) -> List[Dict[str, any]]:
        """
        Get recent commit history.
        
        Args:
            max_commits (int): Maximum number of commits to return
            
        Returns:
            List of commit information dictionaries
        """
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits('HEAD', max_count=max_commits):
                commits.append({
                    "hash": commit.hexsha[:8],
                    "author": commit.author.name,
                    "date": commit.committed_datetime.isoformat(),
                    "message": commit.message.strip(),
                    "files_changed": len(commit.stats.files)
                })
            return commits
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_branches(self) -> List[Dict[str, any]]:
        """
        Get list of all branches.
        
        Returns:
            List of branch information dictionaries
        """
        if not self.repo:
            return []
        
        try:
            branches = []
            for branch in self.repo.branches:
                branches.append({
                    "name": branch.name,
                    "is_active": branch.name == self.repo.active_branch.name,
                    "last_commit": branch.commit.hexsha[:8],
                    "last_commit_date": branch.commit.committed_datetime.isoformat()
                })
            return branches
        except Exception as e:
            return [{"error": str(e)}]
    
    def get_diff(self, commit_hash: str = None) -> str:
        """
        Get diff for a specific commit or working directory.
        
        Args:
            commit_hash (str): Commit hash to diff against (defaults to HEAD)
            
        Returns:
            String containing the diff output
        """
        if not self.repo:
            return "Not a Git repository"
        
        try:
            if commit_hash:
                # Diff between two commits
                commit = self.repo.commit(commit_hash)
                parent = commit.parents[0] if commit.parents else None
                if parent:
                    return self.repo.git.diff(parent.hexsha, commit.hexsha)
                else:
                    return "Initial commit - no diff available"
            else:
                # Diff of working directory
                return self.repo.git.diff()
        except Exception as e:
            return f"Error getting diff: {str(e)}"
    
    def get_file_history(self, file_path: str, max_commits: int = 5) -> List[Dict[str, any]]:
        """
        Get commit history for a specific file.
        
        Args:
            file_path (str): Path to the file
            max_commits (int): Maximum number of commits to return
            
        Returns:
            List of commit information for the file
        """
        if not self.repo:
            return []
        
        try:
            commits = []
            for commit in self.repo.iter_commits('HEAD', paths=file_path, max_count=max_commits):
                commits.append({
                    "hash": commit.hexsha[:8],
                    "date": commit.committed_datetime.isoformat(),
                    "message": commit.message.strip(),
                    "author": commit.author.name
                })
            return commits
        except Exception as e:
            return [{"error": str(e)}]

# Convenience functions for easy access
def get_git_status(repo_path: str = None) -> Dict[str, any]:
    """Get Git status for a repository."""
    if not GIT_AVAILABLE:
        return {"error": "GitPython is not available. Install with: pip install gitpython"}
    
    try:
        git_mgr = GitManager(repo_path)
        return git_mgr.get_status()
    except Exception as e:
        return {"error": str(e)}

def get_recent_commits(repo_path: str = None, max_commits: int = 10) -> List[Dict[str, any]]:
    """Get recent commit history for a repository."""
    if not GIT_AVAILABLE:
        return [{"error": "GitPython is not available. Install with: pip install gitpython"}]
    
    try:
        git_mgr = GitManager(repo_path)
        return git_mgr.get_commit_history(max_commits)
    except Exception as e:
        return [{"error": str(e)}]

def list_branches(repo_path: str = None) -> List[Dict[str, any]]:
    """List all branches in a repository."""
    if not GIT_AVAILABLE:
        return [{"error": "GitPython is not available. Install with: pip install gitpython"}]
    
    try:
        git_mgr = GitManager(repo_path)
        return git_mgr.get_branches()
    except Exception as e:
        return [{"error": str(e)}]
