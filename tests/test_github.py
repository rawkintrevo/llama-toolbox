import pytest
from llama_toolbox.github import CommitFile, CreateIssue, GetRepoContents, ReadIssue, SearchRepos

def test_commit_file():
    commit_file = CommitFile(api_key="your_api_key_here")
    result = commit_file.fn("https://github.com/rawkintrevo/llama-toolbox", "example.txt", "Hello World!", "Added example.txt")
    assert result is not None

def test_create_issue():
    create_issue = CreateIssue(api_key="your_api_key_here")
    issue_url = create_issue.fn("https://github.com/rawkintrevo/llama-toolbox", "New issue", "This is a new issue")
    assert issue_url is not None

def test_get_repo_contents():
    get_repo_contents = GetRepoContents(api_key="your_api_key_here")
    contents = get_repo_contents.fn("https://github.com/rawkintrevo/llama-toolbox")
    assert contents is not None

def test_read_issue():
    read_issue = ReadIssue(api_key="your_api_key_here")
    result = read_issue.fn("https://github.com/rawkintrevo/llama-toolbox", 123)
    assert result is not None

def test_search_repos():
    search_repos = SearchRepos(api_key="your_api_key_here")
    results = search_repos.fn("machine learning")
    assert results is not None