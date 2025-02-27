# XCryptoWatch

XCryptoWatch is a powerful Python tool that monitors social media platforms (Twitter, Truth Social, and Bluesky) for cryptocurrency-related posts from specified accounts. It uses OpenAI's GPT to analyze posts and can notify users via email when relevant cryptocurrency content is detected.

## Features

- Multi-platform social media monitoring:
  - Twitter
  - Truth Social
  - Bluesky
- AI-powered post analysis using OpenAI's GPT
- Flexible notification system:
  - Postal API support
  - SMTP email support
- Configurable monitoring intervals
- Interactive command-line interface
- Comprehensive logging system

## Installation

To install XCryptoWatch, simply run:

```bash
pip install xcryptowatch
```

## Requirements

- Python 3.9 or higher
- Required packages (automatically installed):
  - postalsend
  - jsonschema
  - tweepy
  - openai
  - truthbrush
  - atproto

## Configuration

XCryptoWatch requires a configuration file (`config.json`) with your API credentials and settings. On first run, the program will guide you through creating this configuration.

Required credentials:
- Twitter API credentials (optional)
- Truth Social credentials (optional)
- Bluesky credentials (optional)
- OpenAI API key
- Email settings (SMTP or Postal)

## Usage

1. Start XCryptoWatch:

```bash
xcryptowatch
```

2. Use the interactive menu to:
- Start/stop watching different platforms
- Add new accounts to monitor
- Add notification recipients
- Configure API credentials and settings

## Menu Options

1. Start watching tweets
2. Stop watching tweets
3. Start watching truths
4. Stop watching truths
5. Start watching bluesky
6. Stop watching bluesky
7. Add a new account to watch
8. Add a new recipient to notify
9. Configure XCryptoWatch

## Configuration Options

The configuration interface allows you to set:
- Social media API credentials
- Monitoring intervals
- Email notification settings
- OpenAI API key

## Development

```bash
git clone https://github.com/steelproxy/xcryptowatch.git
cd xcryptowatch
pip install -e .
```

## License

MIT License - see LICENSE file for details.

## Author

Collin Rodes (steelproxy@protonmail.com)

## Version

Current version: 0.1.1

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## Security Note

Keep your `config.json` file secure as it contains sensitive API credentials. The file is automatically added to `.gitignore` to prevent accidental commits.

