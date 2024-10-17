import requests
import json
from datetime import datetime
from urllib.parse import urlparse
import sys
import re
from typing import Dict, Tuple, Optional, Any, List

def print_colored(text: str, color: str) -> None:
    """
    Print colored text.

    Args:
        text: Text to be printed.
        color: Color to be applied to the text.
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
    print(colored_text)

def input_colored(prompt: str, color: str) -> str:
    """
    Get user input with colored prompt.

    Args:
        prompt: Prompt to be displayed to the user.
        color: Color of the prompt.

    Returns:
        User input.
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
    """
    Get base URL from user input.

    Returns:
        Base URL.
    """
    base_url: str = input_colored("Enter IPTV link: ", "cyan")
    parsed_url: urlparse = urlparse(base_url)
    host: str = parsed_url.hostname
    port: Optional[int] = parsed_url.port

    if port is None:
        port = 80

    return f"http://{host}:{port}"

def get_mac_address() -> str:
    """
    Get MAC address from user input.

    Returns:
        MAC address.
    """
    return input_colored("Input Mac address: ", "cyan").upper()

def get_token(session: requests.Session, base_url: str, timeout: int = 10) -> Optional[str]:
    """
    Get token for authentication.

    Args:
        session: Requests session object.
        base_url: Base URL of the IPTV service.
        timeout: Timeout for the request.

    Returns:
        Authentication token or None if unsuccessful.
    """
    url: str = f"{base_url}/portal.php?action=handshake&type=stb&token=&JsHttpRequest=1-xml"
    try:
        res: requests.Response = session.get(url, timeout=timeout, allow_redirects=False)
        data: Dict[str, Any] = json.loads(res.text)
        return data['js']['token']
    except (requests.RequestException, json.JSONDecodeError) as e:
        print_colored(f"Error fetching token: {e}", "red")
        return None

def get_subscription(session: requests.Session, base_url: str, token: str, timeout: int = 10) -> bool:
    """
    Get subscription information.

    Args:
        session: Requests session object.
        base_url: Base URL of the IPTV service.
        token: Authentication token.
        timeout: Timeout for the request.

    Returns:
        True if successful, False otherwise.
    """
    url: str = f"{base_url}/portal.php?type=account_info&action=get_main_info&JsHttpRequest=1-xml"
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {token}"
    }
    try:
        res: requests.Response = session.get(url, headers=headers, timeout=timeout, allow_redirects=False)
        if res.status_code == 200:
            data: Dict[str, Any] = json.loads(res.text)
            mac: str = data['js']['mac']
            expiry: str = data['js']['phone']
            print_colored(f"MAC = {mac}\nExpiry = {expiry}", "green")
            return True
        else:
            print_colored("Failed to fetch subscription info", "red")
            return False
    except requests.RequestException as e:
        print_colored(f"Error fetching subscription info: {e}", "red")
        return False

def get_channel_list(session: requests.Session, base_url: str, headers: Dict[str, str], timeout: int = 10) -> Tuple[Optional[List[Dict[str, Any]]], Optional[Dict[int, str]]]:
    """
    Get channel list.

    Args:
        session: Requests session object.
        base_url: Base URL of the IPTV service.
        headers: Headers for the request.
        timeout: Timeout for the request.

    Returns:
        Tuple containing channels data and group information.
    """
    url_genre: str = f"{base_url}/server/load.php?type=itv&action=get_genres&JsHttpRequest=1-xml"
    try:
        res_genre: requests.Response = session.get(url_genre, headers=headers, timeout=timeout, allow_redirects=False)
        group_info: Dict[int, str] = {}
        if res_genre.status_code == 200:
            id_genre: List[Dict[str, Any]] = json.loads(res_genre.text)['js']
            group_info = {group['id']: group['title'] for group in id_genre}
            url3: str = f"{base_url}/portal.php?type=itv&action=get_all_channels&JsHttpRequest=1-xml"
            res3: requests.Response = session.get(url3, headers=headers, timeout=timeout, allow_redirects=False)
            if res3.status_code == 200:
                channels_data: List[Dict[str, Any]] = json.loads(res3.text)["js"]["data"]
                return channels_data, group_info
            else:
                print_colored("Failed to fetch channel list", "red")
                return None, None
        else:
            print_colored("Failed to fetch group info", "red")
            return None, None
    except requests.RequestException as e:
        print_colored(f"Error fetching channel list: {e}", "red")
        return None, None

def save_channel_list(base_url: str, current: str, channels_data: List[Dict[str, Any]], group_info: Dict[int, str], mac: str) -> None:
    """
    Save channel list to a file.

    Args:
        base_url: Base URL of the IPTV service.
        current: Current timestamp.
        channels_data: List of channel data.
        group_info: Dictionary containing group information.
        mac: MAC address.

    Returns:
        None.
    """
    sanitized_url: str = base_url.replace("://", "_").replace("/", "_").replace(".", "_").replace(":", "_")
    try:
        with open(f'{sanitized_url}_{current}.m3u', 'w', encoding='utf-16') as file:
            file.write('#EXTM3U\n')
            count: int = 0
            for channel in channels_data:
                group_id: int = channel['tv_genre_id']
                group_name: str = group_info.get(group_id, "General")
                name: str = channel['name']
                logo: str = channel.get('logo', '')
                cmd_url: str = channel['cmds'][0]['url'].replace('ffmpeg ', '')
                if "localhost" in cmd_url:
                    ch_id_match: Optional[re.Match] = re.search(r'/ch/(\d+)_', cmd_url)
                    if ch_id_match:
                        ch_id: str = ch_id_match.group(1)
                        cmd_url = f"{base_url}/play/live.php?mac={mac}&stream={ch_id}&extension=ts"

                channel_str: str = f'#EXTINF:-1 tvg-logo="{logo}" group-title="{group_name}",{name}\n{cmd_url}\n'
                count += 1
                file.write(channel_str)
            print_colored(f"Channels = {count}", "green")
            print_colored(f"\nChannel list has been dumped to {sanitized_url}_{current}.m3u", "blue")
    except IOError as e:
        print_colored(f"Error saving channel list: {e}", "red")

def main() -> None:
    """
    Main function to orchestrate the process.
    """
    try:
        base_url: str = get_base_url()
        mac: str = get_mac_address()
        session: requests.Session = requests.Session()
        session.cookies.update({'mac': f'{mac}'})
        token: Optional[str] = get_token(session, base_url)
        if token:
            if get_subscription(session, base_url, token):
                headers: Dict[str, str] = {
                    "Authorization": f"Bearer {token}"
                }
                channels_data, group_info = get_channel_list(session, base_url, headers)
                if channels_data and group_info:
                    current: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    save_channel_list(base_url, current, channels_data, group_info, mac)
    except KeyboardInterrupt:
        print_colored("\nExiting gracefully...", "yellow")
        sys.exit(0)

if __name__ == "__main__":
    main()