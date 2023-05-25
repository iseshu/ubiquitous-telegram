# Ubiquitous Telegram Bot

![Logo](thumb.jpg)

Ubiquitous Telegram Bot is a Python bot built using the Pyrogram library. It scrapes download links, downloads files to the server, and sends them to Telegram.

## Features

- Scrapes download links from specified sources.
- Downloads files to the server.
- Sends downloaded files to Telegram.

## Deployment

You can deploy the Ubiquitous Telegram Bot to Heroku with a single click using the Heroku Deploy button.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/iseshu/ubiquitous-telegram)

1. Click the **Deploy to Heroku** button above.
2. Fill in the required environment variables (`API_ID`, `API_HASH`, `BOT_TOKEN`, `DUMP_ID`, `DATABASE_URL`).
3. Choose an app name, region, and any additional configurations.
4. Click **Deploy**.

Heroku will build and deploy the bot using the provided repository. Once the deployment is complete, you can start using the bot on your Telegram account.

## Usage

1. Start the bot on your Telegram account.
2. Send it download links or specific commands to trigger the scraping and file sending functionality.

## License

This project is licensed under the [MIT License](LICENSE).
