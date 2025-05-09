import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# GitHub API endpoints
GITHUB_API_SEARCH_ENDPOINT = "https://api.github.com/search/repositories"
GITHUB_API_REPO_ENDPOINT = "https://api.github.com/repos/{owner}/{repo_name}"

# Maximum number of results to return per page
PER_PAGE = 30

# Default values for query parameters
DEFAULT_QUERY = ""
DEFAULT_LANGUAGE = None
DEFAULT_SORT = "stars"


@app.route("/search_repositories", methods=["GET"])
def search_repositories():
    # Get the query parameters
    q = request.args.get("q") or DEFAULT_QUERY
    page = int(request.args.get("page")) if request.args.get("page") else 1
    language = request.args.get("language") or DEFAULT_LANGUAGE
    sort = request.args.get("sort") or DEFAULT_SORT

    # Build the GitHub API query string
    query = f"{GITHUB_API_SEARCH_ENDPOINT}?q={q}&page={page}&per_page={PER_PAGE}"
    if language:
        query += f"&language={language}"
    if sort:
        query += f"&sort={sort}"

    # Make the API request to GitHub
    response = requests.get(query)

    # Check for errors and return appropriate status codes
    if response.status_code == 400:
        return "Invalid query", 400
    elif response.status_code == 404:
        return "No results found", 404
    elif response.status_code != 200:
        return f"Error {response.status_code}", response.status_code

    # Parse the JSON response from GitHub
    data = response.json()

    # Build a list of repositories with the desired details
    repositories = []
    for repository in data["items"]:
        repositories.append({
            "name": repository["full_name"],
            "description": repository["description"],
            "stars": repository["stargazers_count"],
            "forks": repository["forks_count"],
            "language": repository["language"]
        })

    # Paginate the results if necessary
    pagination = {}
    if data["total_count"] > PER_PAGE:
        num_pages = int(data["total_count"] / PER_PAGE) + 1
        pagination = {
            "total": data["total_count"],
            "per_page": PER_PAGE,
            "current_page": page,
            "last_page": num_pages,
            "next_page": f"{request.url}?q={q}&page={page + 1}" if page < num_pages else None,
        }

    # Return the results as JSON
    return jsonify({
        "repositories": repositories,
        "pagination": pagination
    })


@app.route("/repo_details/<string:owner>/<string:repo_name>", methods=["GET"])
def get_repo_details(owner, repo_name):
    # Make a request to GitHub's API to fetch repository details
    response = requests.get(GITHUB_API_REPO_ENDPOINT.format(owner=owner, repo_name=repo_name))

    # Check for errors and return appropriate status codes
    if response.status_code == 404:
        return "Repository not found", 404
    elif response.status_code != 200:
        return f"Error {response.status_code}", response.status_code

    # Extract and return the desired data
    repo = response.json()

    # Get the list of contributors from a separate API call
    contributors_response = requests.get(repo["contributors_url"])
    if contributors_response.status_code == 200:
        contributors = [{"name": contributor["login"], "contributions": contributor["contributions"]} for contributor in contributors_response.json()]
    else:
        contributors = []

    # Get the list of recent commits (up to 5)
    commits_response = requests.get(f"{repo['commits_url'].split('{/sha}')[0]}?per_page=5")
    if commits_response.status_code == 200:
        commits = [{"message": commit["commit"]["message"], "date": commit["commit"]["author"]["date"]} for commit in commits_response.json()]
    else:
        commits = []

    return jsonify({
        "open_issues": repo["open_issues"],
        "open_pull_requests": repo["open_pull_requests"],
        "contributors": contributors,
        "recent_commits": commits
    })


if __name__ == "__main__":
    app.run(debug=True)

