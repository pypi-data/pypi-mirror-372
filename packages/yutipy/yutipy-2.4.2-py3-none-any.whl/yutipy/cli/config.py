import os
import webbrowser

from dotenv import load_dotenv, set_key


def run_config_wizard():
    """Interactive configuration wizard for setting up API keys."""
    print("Welcome to the yutipy Configuration Wizard!")
    print("This wizard will help you set up your API keys for various services.\n")

    # Load existing .env file if it exists
    env_file = ".env"
    load_dotenv(env_file)

    # List of available services and their required environment variables
    services = {
        "Spotify": {
            "SPOTIFY_CLIENT_ID": {
                "description": "Spotify Client ID",
                "url": "https://developer.spotify.com/dashboard",
                "instructions": """
1. Go to your Spotify Developer Dashboard: https://developer.spotify.com/dashboard
2. Create a new app and fill in the required details.
3. Copy the "Client ID" and "Client Secret" from the app's settings.
4. Paste them here when prompted.
                """,
            },
            "SPOTIFY_CLIENT_SECRET": {
                "description": "Spotify Client Secret",
                "url": "https://developer.spotify.com/dashboard",
                "instructions": "See the steps above for Spotify Client ID.",
            },
        },
        "KKBox": {
            "KKBOX_CLIENT_ID": {
                "description": "KKBox Client ID",
                "url": "https://developer.kkbox.com/",
                "instructions": """
1. Go to the KKBOX Developer Portal: https://developer.kkbox.com/
2. Log in and create a new application.
3. Copy the "Client ID" and "Client Secret" from the app's settings.
4. Paste them here when prompted.
                """,
            },
            "KKBOX_CLIENT_SECRET": {
                "description": "KKBox Client Secret",
                "url": "https://developer.kkbox.com/",
                "instructions": "See the steps above for KKBox Client ID.",
            },
        },
        "Last.fm": {
            "LASTFM_API_KEY": {
                "description": "Last.fm API Key",
                "url": "https://www.last.fm/api/account/create",
                "instructions": """
1. Go to the Last.fm API account creation page: https://www.last.fm/api/account/create
2. Log in with your Last.fm account.
3. Create a new application and fill in the required details.
4. Copy the "API Key" from the application settings.
5. Paste it here when prompted.
                """,
            },
        },
    }

    # Display available services
    print("Available services:")
    for i, service in enumerate(services.keys(), start=1):
        print(f"{i}. {service}")

    # Prompt the user to select a service
    choice = input("\nEnter the number of the service you want to configure: ").strip()
    try:
        service_name = list(services.keys())[int(choice) - 1]
    except (IndexError, ValueError):
        print("Invalid choice. Exiting configuration wizard.")
        return

    print(f"\nYou selected: {service_name}")

    # Get the selected service's variables
    selected_service = services[service_name]

    # Track whether the browser has already been opened for a service
    browser_opened = set()

    # Prompt the user for each variable in the selected service
    for var, details in selected_service.items():
        current_value = os.getenv(var)
        if current_value:
            print(f"{details['description']} is already set.")
            continue

        print(f"\n{details['description']} is missing.")
        print(details["instructions"])

        # Check if the browser has already been opened for this service
        if details["url"] not in browser_opened:
            open_browser = (
                input(
                    f"Do you want to open the website to get your {details['description']}? (y/N): "
                )
                .strip()
                .lower()
            )
            if open_browser == "y":
                webbrowser.open(details["url"])
                print(f"The website has been opened in your browser: {details['url']}")
                browser_opened.add(details["url"])  # Mark this URL as opened

        # Prompt the user to enter the value
        new_value = input(f"Enter your {details['description']}: ").strip()
        if new_value:
            set_key(env_file, var, new_value)
            print(f"{details['description']} has been saved to the .env file.")

    print("\nConfiguration complete! Your API keys have been saved to the .env file.")


if __name__ == "__main__":
    run_config_wizard()
