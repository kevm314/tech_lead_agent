from github import Github

# Authentication is defined via github.Auth
from github import Auth


class GithubConnector:
    def __init__(self, github_access_token):
        self.github_access_token = github_access_token

    def create_ticket_from_json(self, json_dict: dict, repo_name: str):
        return self.create_sweep_ticket(json_dict['title'], json_dict['description'], json_dict['tags'], repo_name)

    def create_sweep_ticket(self, title: str, description: str, tags: list, repo_name: str):
        # using an access token
        auth = Auth.Token(self.github_access_token)

        # Public Web Github
        g = Github(auth=auth)

        # Then play with your Github objects:
        repo = g.get_repo(repo_name)

        repo.create_issue(title="Sweep:" + title, body=description, labels=tags)

        # To close connections after use
        g.close()