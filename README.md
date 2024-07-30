# IPTV Mac to M3U Converter

## Overview
This repository contains three Python scripts, `maclist.py`, `macvod.py`, and `macshow.py`, for converting IPTV server links and Mac addresses into M3U playlist files.

- **`maclist.py`**: Takes input of an IPTV server link and a Mac address, and returns the Mac address, subscription expiry, and the number of channels associated with it. It then constructs an M3U playlist file containing all the channels ready to be used with M3U players.
- **`macvod.py`**: Takes input of an IPTV server link and a Mac address, retrieves VOD (Video On Demand) categories and items, and constructs an M3U playlist file containing all the VOD items ready to be used with M3U players.
- **`macshow.py`**: Takes input of an IPTV server link and a Mac address, retrieves TV series categories, seasons, and episodes, and constructs an M3U playlist file containing all the episodes ready to be used with M3U players.

## Features
- Takes input of IPTV server link and Mac address
- Retrieves subscription information and channel/VOD/TV series list
- Constructs an M3U playlist file with channel/VOD/TV series information

## Requirements
- Python 3.x
- requests library (`pip install requests`)
- tqdm library (`pip install tqdm`)
- aiohttp library (`pip install aiohttp`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/fairy-root/mac-to-m3u.git
   cd mac-to-m3u
   ```
2. Install dependencies:
   ```bash
   pip install requests tqdm aiohttp
   ```

## Usage

### maclist.py
1. Run the script:
   ```bash
   python maclist.py
   ```
2. Follow the prompts to enter the IPTV link and Mac address.
3. The script will retrieve subscription information, fetch the channel list, and construct an M3U playlist file.

### macvod.py
1. Run the script:
   ```bash
   python macvod.py
   ```
2. Follow the prompts to enter the IPTV link and Mac address.
3. The script will retrieve subscription information, fetch the VOD categories and items, and construct an M3U playlist file.

### macshow.py
1. Run the script:
   ```bash
   python macshow.py
   ```
2. Follow the prompts to enter the IPTV link and Mac address.
3. The script will retrieve subscription information, fetch the TV series categories, seasons, and episodes, and construct an M3U playlist file.

## Note
- Ensure the IPTV link is accessible and correctly formatted.
- Interrupting the script (e.g., with Ctrl+C) will gracefully exit the process.

## Donation

Your support is appreciated:

- USDt (TRC20): `TGCVbSSJbwL5nyXqMuKY839LJ5q5ygn2uS`
- BTC: `13GS1ixn2uQAmFQkte6qA5p1MQtMXre6MT`
- ETH (ERC20): `0xdbc7a7dafbb333773a5866ccf7a74da15ee654cc`
- LTC: `Ldb6SDxUMEdYQQfRhSA3zi4dCUtfUdsPou`

## Author

- [GitHub: FairyRoot](https://github.com/fairy-root)
- [Telegram: @FairyRoot](https://t.me/FairyRoot)

## Contributing

If you have suggestions or improvements, please fork the repository and create a pull request or open an issue.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.