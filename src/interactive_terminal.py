import os
import pathlib

from dotenv import load_dotenv

from AgentSmith import AgentSmith
from utils import extract_repo_name


load_dotenv(dotenv_path=pathlib.Path('../.env'))


def main():
    repo_urls = []  # List to hold the provided URLs

    print("Agent Smith: A Software Project Manager for creating Github Issues.")
    print("Let's start with listing the repos that we are looking at:")

    while True:  # Infinite loop

        user_input = input("Enter a GitHub repo URL (or type 'done' to finish): ").strip()

        if user_input.lower() == 'exit' or user_input == '':
            break  # Exit the loop if the user types 'exit'
        elif user_input:
            repo_urls.append(user_input)  # Add the URL to the list if it's not an empty string

    # Output the collected URLs
    print("\nCollected GitHub repo URLs:")
    for i, url in enumerate(repo_urls, 1):
        print(f"{i}. {url}")

    agent_smith = AgentSmith()

    print("Clone Repos into temp location")

    for i, url in enumerate(repo_urls, 1):
        agent_smith.add_git_repo_as_vector_store(url)

    agent_smith.init_agent()

    feature_request = input("What feature request would you like to add? ").strip()

    agent_smith.run(feature_request)




if __name__ == "__main__":
    main()
