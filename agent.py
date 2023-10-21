# Load ELD from text file
from GithubConnector import GithubConnector


def load_text_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Load File information from Github
# TODO

# Load prompt guide

prompt_guide = "You are a tech lead, you have access to multiple repos, given a feature request, your job is to go through the code files and create a list of tickets for a software engineer to work on"

# Create tickets (as per prompt)


# Ask if user is happy with prompt or would like to improve on them

# If user is happy, create tickets
def get_user_confirmation(template):
    print("Here is the generated GitHub issue template:")
    print(template)
    user_response = input("Are you happy with this template? (yes/no): ").strip().lower()
    return user_response == 'yes'

# Get user confirmation
issue_template = ""
is_confirmed = get_user_confirmation(issue_template)

if is_confirmed:
    print("User confirmed. Proceed to create the GitHub issue.")
    github_connector = GithubConnector("", None)

    for ticket in issue_templates:
        github_connector.create_ticket_from_json(ticket)

else:
    print("User not satisfied. Provide options to edit the template.")


# If user is not happy, add feedback to prompt and rerun
