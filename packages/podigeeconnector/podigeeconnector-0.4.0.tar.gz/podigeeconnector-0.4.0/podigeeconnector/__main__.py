"""
This is the main entry point for the Podigee Connector.
"""

import json
import os
from loguru import logger
from .connector import PodigeeConnector


def load_env_var(var_name: str) -> str:
    """
    Load environment variable or throw error
    """
    var = os.environ.get(var_name)
    if var is None or var == "":
        raise ValueError(f"Environment variable {var_name} must be set.")
    return var


def main():
    """
    Main entry point for the Podigee Connector.
    """
    base_url = load_env_var("PODIGEE_BASE_URL")
    podcast_id = os.environ.get("PODCAST_ID")

    # This can be empty, in which case the session token will be used
    podigee_access_token = os.environ.get("PODIGEE_ACCESS_TOKEN")

    # This can be empty, in which case the username and password will be used
    podigee_session_v5 = os.environ.get("PODIGEE_SESSION_V5")

    if podigee_access_token:
        logger.info("Using Podigee Access Token for authentication")
        logger.debug("Token = {}...", podigee_access_token[:8])
        connector = PodigeeConnector(
            base_url=base_url,
            podigee_access_token=podigee_access_token,
        )
    elif podigee_session_v5:
        logger.info("Using Podigee Session V5 for authentication")
        # Fallback: Use session token to log in
        connector = PodigeeConnector(
            base_url,
            podigee_session_v5,
        )
    else:
        # Fallback: Use username and password to log in
        logger.info("Using Podigee Username and Password for authentication")
        username = load_env_var("PODIGEE_USERNAME")
        password = load_env_var("PODIGEE_PASSWORD")
        connector = PodigeeConnector.from_credentials(
            base_url=base_url,
            username=username,
            password=password,
        )

    podcasts = connector.podcasts()
    logger.info("Podcasts = {}", json.dumps(podcasts, indent=4))

    if not podcasts:
        logger.error("No podcasts found")
        return

    # If no specific podcast ID is provided, list all podcasts and exit
    if not podcast_id:
        logger.info("No PODCAST_ID provided. Listing all available podcasts:")
        for podcast in podcasts:
            logger.info(
                "Podcast ID: {}, Title: {}, Last Episode: {}",
                podcast["id"],
                podcast["title"],
                podcast.get("last_episode_publication_date", "N/A"),
            )
        return

    # Find the specific podcast by ID
    selected_podcast = None
    for podcast in podcasts:
        if str(podcast["id"]) == str(podcast_id):
            selected_podcast = podcast
            break

    if not selected_podcast:
        logger.error("Podcast with ID {} not found", podcast_id)
        logger.info("Available podcast IDs:")
        for podcast in podcasts:
            logger.info("  - {}: {}", podcast["id"], podcast["title"])
        return

    podcast_id = selected_podcast["id"]
    logger.info("Using podcast {}: {}", podcast_id, selected_podcast["title"])

    podcast_overview = connector.podcast_overview(podcast_id)
    logger.info("Podcast Overview = {}", json.dumps(podcast_overview, indent=4))

    podcast_totals = connector.podcast_totals(podcast_id)
    logger.info("Podcast Totals = {}", json.dumps(podcast_totals, indent=4))
    logger.info("Total Downloads: {}", podcast_totals.get("total_downloads"))
    logger.info("Unique Listeners: {}", podcast_totals.get("unique_listeners_number"))
    logger.info(
        "Unique Subscribers: {}", podcast_totals.get("unique_subscribers_number")
    )

    podcast_analytics = connector.podcast_analytics(podcast_id)
    logger.info("Podcast Analytics = {}", json.dumps(podcast_analytics, indent=4))

    episodes = connector.episodes(podcast_id)
    logger.info("Episodes = {}", json.dumps(episodes, indent=4))

    # Limit episode processing to first 3 episodes to avoid long output
    for episode in episodes[:3]:
        episode_id = episode["id"]
        episode_analytics = connector.episode_analytics(episode_id)
        logger.info(
            "Episode {} = {}", episode_id, json.dumps(episode_analytics, indent=4)
        )

        episode_total = connector.episode_total_downloads(episode_id)
        logger.info("Episode {} Total Downloads: {}", episode_id, episode_total)


if __name__ == "__main__":
    main()
