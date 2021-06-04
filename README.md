# Bookdl Bot

This is my attempt to integrate [libgenesis](https://github.com/Samfun75/libgenesis) (an api for Libgen.rs) to a telegram bot.

## Requirments

- libgenesis  [View](https://github.com/Samfun75/libgenesis)
- Pyrogram [View](https://github.com/pyrogram/pyrogram)
- Pymongo

## Installation

### Heroku

Use the below button to deploy.

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/Samfun75/BookdlBot)

### Other systems

Clone repository

```bash
git clone https://github.com/Samfun75/BookdlBot
```

Change to repository directory

```bash
cd BookdlBot
```

Install requirements and dependencies

```python
pip3 install -r requirements.txt
```

Create a new `config.ini` using the sample available at `bookdl/working_dir/config.ini.sample` in `bookdl/working_dir/`.

```ini
# Here is a sample of config file and what it should include:

# More info on API_ID and API_HASH can be found here: https://docs.pyrogram.org/intro/setup#api-keys

[pyrogram]
api_id = 1234567
api_hash = xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
app_version = 1.0
device_model = PC
system_version = Windows

# Where pyrogram plugins are located

[plugins]
root = bookdl/telegram/plugins


# More info on Bot API Key/token can be found here: https://core.telegram.org/bots#6-botfather

[bot-configuration]
bot_token = 123456789:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
session = BookdlBot
dustbin = -100xxxxxxxxx # Used to store uploaded book. id of a channel where the bot is admin
allowed_users = [123456789, 987654321] # Telegram id of users allowed to use the bot. If the bot is open to all put empty array like this []

# Mongodb Credentials

[database]
db_host = xxxxxxxxxx.xxxxx.mongodb.net or localhost # In this section db_host is the address of the machine where the MongoDB is running
db_username = username
db_password = password
db_name = BookdlBot
db_type = Mongo_Atlas (or Mongo_Community)

# ConvertAPI secret

[convert]
convert_api = secretkey
```

Run bot with

`python -m bookdl`

stop with <kbd>CTRL</kbd>+<kbd>C</kbd>

## Usage

- Send /start and press <kbd>Search 🔍</kbd> and on the open inline query type the book name
- Send a book's MD5 like 'MD5:a382109f7fdde3be5b2cb4f82d97443b'
- Send a book link from 'library.lol, libgen.lc, libgen.gs or b-ok.cc'

After performing one of the above seteps a book detail with 'Download' button is returned and press the button to download and upload the book to telegram.

For books other that PDF, a <kbd>🔃 Convert to PDF</kbd> button is included and it uses converapi to convert the ebook to pdf
