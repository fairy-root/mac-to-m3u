import aiohttp
import asyncio
import json
from datetime import datetime
from urllib.parse import urlparse, quote
import sys
import base64
from typing import Dict, Optional, Any, List
from tqdm import tqdm

def print_colored(text: str, color: str) -> None:
    """Prints text in a specified color using ANSI escape codes.

    Args:
        text (str): The text to be printed.
        color (str): The color to use for the text.
    """
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_text: str = f"{color_code}{text}\033[0m"
    tqdm.write(colored_text)

def input_colored(prompt: str, color: str) -> str:
    """Prompts the user for input with colored text.

    Args:
        prompt (str): The prompt to display.
        color (str): The color to use for the prompt.

    Returns:
        str: The user's input.
    """
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_prompt: str = f"{color_code}{prompt}\033[0m"
    return input(colored_prompt)

def get_base_url() -> str:
    """Prompts the user to enter an IPTV link and returns the base URL.

    Returns:
        str: The base URL of the IPTV link.
    """
    base_url: str = input_colored("Enter IPTV link: ", "cyan")
    parsed_url = urlparse(base_url)
    host: str = parsed_url.hostname or ""
    port: int = parsed_url.port or 80
    return f"http://{host}:{port}"

def get_mac_address() -> str:
    """Prompts the user to enter a MAC address and returns it in uppercase.

    Returns:
        str: The MAC address.
    """
    return input_colored("Input Mac address: ", "cyan").upper()

async def get_token(session: aiohttp.ClientSession, base_url: str, timeout: int = 10) -> Optional[str]:
    """Fetches the authentication token from the IPTV server.

    Args:
        session (aiohttp.ClientSession): The session object.
        base_url (str): The base URL of the IPTV server.
        timeout (int, optional): The request timeout. Defaults to 10.

    Returns:
        Optional[str]: The authentication token or None if an error occurs.
    """
    url: str = f"{base_url}/portal.php?action=handshake&type=stb&token=&JsHttpRequest=1-xml"
    try:
        async with session.get(url, timeout=timeout) as res:
            if res.headers.get('Content-Type', '').startswith('text/javascript'):
                text = await res.text()
                data: Dict[str, Any] = json.loads(text)
                return data['js']['token']
            else:
                print_colored("Unexpected response content type", "red")
                return None
    except (aiohttp.ClientError, json.JSONDecodeError) as e:
        print_colored(f"Error fetching token: {e}", "red")
        return None

async def get_subscription(session: aiohttp.ClientSession, base_url: str, token: str, timeout: int = 10) -> bool:
    """Fetches subscription information from the IPTV server.

    Args:
        session (aiohttp.ClientSession): The session object.
        base_url (str): The base URL of the IPTV server.
        token (str): The authentication token.
        timeout (int, optional): The request timeout. Defaults to 10.

    Returns:
        bool: True if the subscription information is successfully fetched, otherwise False.
    """
    url: str = f"{base_url}/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
    headers: Dict[str, str] = {"Authorization": f"Bearer {token}"}
    try:
        async with session.get(url, headers=headers, timeout=timeout) as res:
            if res.status == 200:
                data: Dict[str, Any] = await res.json(content_type=None)
                mac: str = data['js']['mac']
                expiry: str = data['js']['phone']
                print_colored(f"MAC = {mac}\nExpiry = {expiry}", "green")
                return True
            else:
                print_colored("Failed to fetch subscription info", "red")
                return False
    except aiohttp.ClientError as e:
        print_colored(f"Error fetching subscription info: {e}", "red")
        return False

async def get_series_categories(session: aiohttp.ClientSession, base_url: str, headers: Dict[str, str], timeout: int = 10) -> Optional[List[Dict[str, Any]]]:
    """Fetches series categories from the IPTV server.

    Args:
        session (aiohttp.ClientSession): The session object.
        base_url (str): The base URL of the IPTV server.
        headers (Dict[str, str]): The request headers.
        timeout (int, optional): The request timeout. Defaults to 10.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of series categories or None if an error occurs.
    """
    url: str = f"{base_url}/portal.php?type=series&action=get_categories&JsHttpRequest=1-xml"
    try:
        async with session.get(url, headers=headers, timeout=timeout) as res:
            if res.status == 200:
                data = await res.json(content_type=None)
                categories: List[Dict[str, Any]] = data["js"]
                return [cat for cat in categories if cat['id'] != "*"]
            else:
                print_colored("Failed to fetch series categories", "red")
                return None
    except aiohttp.ClientError as e:
        print_colored(f"Error fetching series categories: {e}", "red")
        return None

async def get_series_list(session: aiohttp.ClientSession, base_url: str, headers: Dict[str, str], category_id: str, page: int = 1, timeout: int = 10) -> Optional[List[Dict[str, Any]]]:
    """Fetches a list of series for a given category from the IPTV server.

    Args:
        session (aiohttp.ClientSession): The session object.
        base_url (str): The base URL of the IPTV server.
        headers (Dict[str, str]): The request headers.
        category_id (str): The ID of the series category.
        page (int, optional): The page number to fetch. Defaults to 1.
        timeout (int, optional): The request timeout. Defaults to 10.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of series or None if an error occurs.
    """
    url: str = (f"{base_url}/portal.php?type=series&action=get_ordered_list&movie_id=0&season_id=0&episode_id=0&row=0&"
                f"JsHttpRequest=1-xml&category={category_id}&sortby=added&fav=0&hd=0&not_ended=0&abc=*&genre=*&years=*&search=&p={page}")
    try:
        async with session.get(url, headers=headers, timeout=timeout) as res:
            if res.status == 200:
                data = await res.json(content_type=None)
                return data["js"]["data"]
            else:
                print_colored("Failed to fetch series list", "red")
                return None
    except aiohttp.ClientError as e:
        print_colored(f"Error fetching series list: {e}", "red")
        return None

async def get_seasons_episodes(session: aiohttp.ClientSession, base_url: str, headers: Dict[str, str], series_id: str, category_id: str, timeout: int = 10) -> Optional[List[Dict[str, Any]]]:
    """Fetches the list of seasons and episodes for a given series from the IPTV server.

    Args:
        session (aiohttp.ClientSession): The session object.
        base_url (str): The base URL of the IPTV server.
        headers (Dict[str, str]): The request headers.
        series_id (str): The ID of the series.
        category_id (str): The ID of the series category.
        timeout (int, optional): The request timeout. Defaults to 10.

    Returns:
        Optional[List[Dict[str, Any]]]: A list of seasons and episodes or None if an error occurs.
    """
    url: str = (f"{base_url}/portal.php?type=series&action=get_ordered_list&movie_id={quote(series_id)}&season_id=0&episode_id=0&row=0&JsHttpRequest=1-xml&category={category_id}&sortby=added&fav=0&hd=0&not_ended=0&abc=*&genre=*&years=*&search=&p=1")
    try:
        async with session.get(url, headers=headers, timeout=timeout) as res:
            if res.status == 200:
                data = await res.json(content_type=None)
                return data["js"]["data"]
            else:
                print_colored("Failed to fetch seasons list", "red")
                return None
    except aiohttp.ClientError as e:
        print_colored(f"Error fetching seasons list: {e}", "red")
        return None

async def fetch_play_link(session: aiohttp.ClientSession, base_url: str, cmd: str, episode_num: int, timeout: int = 10) -> Optional[str]:
    """Fetches the playback link for a specific episode.

    Args:
        session (aiohttp.ClientSession): The session object.
        base_url (str): The base URL of the IPTV server.
        cmd (str): The command string for creating the link.
        episode_num (int): The episode number.
        timeout (int, optional): The request timeout. Defaults to 10.

    Returns:
        Optional[str]: The playback link or None if an error occurs.
    """
    url: str = f"{base_url}/portal.php?type=vod&action=create_link&cmd={quote(cmd)}&series={episode_num}"
    try:
        async with session.get(url, timeout=timeout) as res:
            if res.status == 200:
                data: Dict[str, Any] = await res.json(content_type=None)
                play_url: str = data['js']['cmd'].split(' ')[1]  # Extract the correct part of the URL
                return play_url
            else:
                print_colored("Failed to fetch play link", "red")
                return None
    except aiohttp.ClientError as e:
        print_colored(f"Error fetching play link: {e}", "red")
        return None

def format_episode_number(season_num: int, episode_num: int, total_episodes: int) -> str:
    """Formats the episode number for display.

    Args:
        season_num (int): The season number.
        episode_num (int): The episode number.
        total_episodes (int): The total number of episodes.

    Returns:
        str: The formatted episode number.
    """
    return f"S{season_num} E{episode_num:0{len(str(total_episodes))}d}"

async def save_series_data(file: Any, series_data: List[Dict[str, Any]], session: aiohttp.ClientSession, base_url: str, headers: Dict[str, str], category_title: str) -> int:
    """Saves the series data to a file.

    Args:
        file (Any): The file object to write to.
        series_data (List[Dict[str, Any]]): The series data.
        session (aiohttp.ClientSession): The session object.
        base_url (str): The base URL of the IPTV server.
        headers (Dict[str, str]): The request headers.
        category_title (str): The title of the category.

    Returns:
        int: The total count of episodes saved.
    """
    total_count: int = 0
    for series in series_data:
        series_title: str = series['name']
        series_id: str = series['id'].split(':')[0]
        seasons_data: Optional[List[Dict[str, Any]]] = await get_seasons_episodes(session, base_url, headers, series_id, series['category_id'])
        if seasons_data:
            for season in seasons_data:
                season_num: str = season['id'].split(':')[1]
                episodes: List[int] = season['series']
                total_episodes: int = len(episodes)
                for episode_num in episodes:
                    cmd_data: Dict[str, Any] = {
                        "series_id": series_id,
                        "season_num": int(season_num),
                        "type": "series"
                    }
                    cmd: str = base64.b64encode(json.dumps(cmd_data).encode()).decode()
                    play_link: Optional[str] = await fetch_play_link(session, base_url, cmd, episode_num)
                    if play_link:
                        formatted_episode_num: str = format_episode_number(int(season_num), episode_num, total_episodes)
                        episode_title: str = f"{series_title} {formatted_episode_num}"
                        episode_str: str = (
                            f'#EXTINF:-1 tvg-type="serie" tvg-serie="{series_id}" tvg-season="{season_num}" '
                            f'tvg-episode="{episode_num}" serie-title="{series_title}" '
                            f'tvg-logo="{series.get("screenshot_uri", "")}" group-title="{category_title}",{episode_title}\n{play_link}\n'
                        )
                        file.write(episode_str)
                        total_count += 1
    return total_count

async def fetch_and_save_series(session: aiohttp.ClientSession, base_url: str, headers: Dict[str, str], category: Dict[str, Any], file: Any) -> int:
    """Fetches and saves series data for a given category.

    Args:
        session (aiohttp.ClientSession): The session object.
        base_url (str): The base URL of the IPTV server.
        headers (Dict[str, str]): The request headers.
        category (Dict[str, Any]): The category data.
        file (Any): The file object to write to.

    Returns:
        int: The total count of episodes saved.
    """
    category_id: str = category['id']
    category_title: str = category['title']
    page: int = 1
    total_count: int = 0
    while True:
        series_data: Optional[List[Dict[str, Any]]] = await get_series_list(session, base_url, headers, category_id, page)
        if not series_data:
            break
        count: int = await save_series_data(file, series_data, session, base_url, headers, category_title)
        total_count += count
        page += 1
    return total_count

async def main() -> None:
    """Main function to handle the IPTV data fetching and saving process."""
    try:
        base_url: str = get_base_url()
        mac: str = get_mac_address()
        cookies: Dict[str, str] = {'mac': f'{mac}'}
        async with aiohttp.ClientSession(cookies=cookies) as session:
            token: Optional[str] = await get_token(session, base_url)
            if token:
                if await get_subscription(session, base_url, token):
                    headers: Dict[str, str] = {"Authorization": f"Bearer {token}"}
                    series_categories: Optional[List[Dict[str, Any]]] = await get_series_categories(session, base_url, headers)
                    if series_categories:
                        sanitized_url: str = base_url.replace("://", "_").replace("/", "_").replace(".", "_").replace(":", "_")
                        current: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                        with open(f'{sanitized_url}_{current}.m3u', 'w', encoding='utf-16') as file:
                            file.write('#EXTM3U\n')
                            for category in tqdm(series_categories, desc="Fetching categories"):
                                try:
                                    result: int = await fetch_and_save_series(session, base_url, headers, category, file)
                                    print_colored(f"Fetched {result} episodes for category: {category['title']}", "cyan")
                                except Exception as e:
                                    print_colored(f"Error fetching series for category {category['title']}: {e}", "red")
    except KeyboardInterrupt:
        print_colored("\nExiting gracefully...", "yellow")
        sys.exit(0)
    except Exception as e:
        print_colored(f"Unexpected error: {e}", "red")
        await main()

if __name__ == "__main__":
    asyncio.run(main())