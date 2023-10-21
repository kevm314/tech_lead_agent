import json
import os

from GithubConnector import GithubConnector


def create_ticket(title: str, description: str, affected_files=None, tags=None, repo_name: str = ""):
    """Create a ticket or code feature request as an output JSON file. with the given input parameters"""

    if tags is None:
        tags = []
    if affected_files is None:
        affected_files = []

    output_folder = "./tickets/"
    # Create a ticket dictionary with the provided details
    ticket = {
        "title": title,
        "description": description,
        "affected_files": affected_files,
        "tags": tags,
        "status": "Open"
    }

    # Generate a unique filename based on the title
    filename = title.replace(" ", "_") + ".json"
    filepath = os.path.join(output_folder, filename)

    # Write the ticket to a JSON file
    with open(filepath, 'w') as file:
        json.dump(ticket, file, indent=4)

    ticket["description"] += " Files to edit: " + str(ticket["affected_files"])
    github_connector = GithubConnector(github_access_token=os.getenv("GITHUB_KEY"))

    github_connector.create_ticket_from_json(ticket, repo_name=repo_name)

    return f"Ticket saved to {filepath}"

