# IPTV Mac to M3U Converter

## Overview
This Python script, `maclist.py`, takes input of an IPTV server link and a Mac address, and returns the Mac address, subscription expiry, and the number of channels associated with it. It then constructs an M3U playlist file containing all the channels ready to be used with M3U players.

## Features
- Takes input of IPTV server link and Mac address
- Retrieves subscription information and channel list
- Constructs an M3U playlist file with channel information

## Added by Contribution
### Sadorowo
- Added ability to select categories which should be exported
- Script is asking for them after genre fetching
- All available categories are displayed for user, separated by comma (,)
- User must type wanted categories in this format:
```yaml
Category 1, Category 2
```
or, if a single category is provided:
```yaml
Category 1
```

If category name isn't in categories fetched by script, user must provide them again.
- User can omit this field if user want to export all categories - just leave them blank 

## Requirements
- Python 3.x
- requests library (`pip install requests`)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/fairy-root/mac-to-m3u.git
   cd mac-to-m3u
   ```
2. Install dependencies:
   ```bash
   pip install requests
   ```

## Usage
1. Run the script:
   ```bash
   python maclist.py
   ```
2. Follow the prompts to enter the IPTV link, Mac address and (optionally) categories you want to export.
3. The script will retrieve subscription information, fetch the channel list, and construct an M3U playlist file.

## Note
- Ensure the IPTV link is accessible and correctly formatted.
- Interrupting the script (e.g., with Ctrl+C) will gracefully exit the process.

## Donation

Your support is appreciated:

- USDt (TRC20): `TGCVbSSJbwL5nyXqMuKY839LJ5q5ygn2uS`
- BTC: `13GS1ixn2uQAmFQkte6qA5p1MQtMXre6MT`
- ETH (ERC20): `0xdbc7a7dafbb333773a5866ccf7a74da15ee654cc`
- LTC: `Ldb6SDxUMEdYQQfRhSA3zi4dCUtfUdsPou`


## Contributing

If you have suggestions or improvements, please fork the repository and create a pull request or open an issue.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
