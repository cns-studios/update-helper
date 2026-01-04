#  Update Helper controlled by a Discord bot

## Usage

### Commands
Type your command into a DC Chat, where the bot is installed.
**Available Commands**
- `!update all [TIME]`
- `!update [PROJECT] [TIME]`
- `!update [GROUP] [TIME]`

The `[TIME]` is defined in hours, to scedule updates.

### Update Configuration

To add Projects that can be individually updated, edit the `webhook_handler.py` file:
```python
if target == 'all':
  cmd = ['bash', '/path/to/update_all.sh']
elif target == 'project':
  cmd = ['bash', '/path/to/update_project.sh']
elif target == 'group':
  cmd = ['bash', '/path/to/update_group.sh']
```


And example update file would look like this:
```bash
#!/bin/bash
echo "Starting full system update..."
docker compose -f /path/to/docker-compose.yml pull
docker compose -f /path/to/docker-compose.yml up -d
echo "Update completed at $(date)"
```

But any bash script will work.

**Be aware that anyone, that has access to the Bot commands can run anything you've configured on your Server!**

### Discord Webhook

To get your **Discord Webhook URL**, follow these steps:

- Go to your Discord Channel, where the Bot is installed
- Settings -> Integrations -> Webhooks
- Copy a new Webhook and paste the URL into a file named `.env`

**The .env File** should look like this:

```
DC_WEBHOOK_URL=https://discordapp.com/api/webhooks/...
```

## Configuration

Maybe youre using `cloudflared` or other Tunnels. Either way you have to expose the `Webhook URl` to the Internet somehow. You could open Ports on your Firewall and Router or setup tunneling Rules in your Tunnel Provider.

### Advanced
An example for `cloudflare tunnels`:
```bash
cloudflared tunnel route dns your-tunnel updates.yourdomain.com
```

Then your Discord Bot would use:
`DC_WEBHOOK_URL="https://updates.yourdomain.com`


To change the default listener for the Webhook, add this to `your .env File`:

```
PORT=YOURPORT
```


## Create the Discord Bot

You have to create a bot that youre adding to your Server. Heres how to do that:

- Go to the (Discord Developer Page)[https://discord.com/developers/applications]
- Click `New Application`
- Give it a name e.g. `Update Manager`
- Click `Create`
- In the left sidebar, click `Bot`
- Under the Bots username, click `Reset Token` and copy the newly created one
- **Save this Token** - youll need that
- Scroll down and enable these `Privileged Gateway Intents`:
  - Message Content Intent (Only that one lol)
- Go to `OAuth2` -> `URL Generator` in the left sidebar
- Under `SCOPES`, check **bot**
- Under `BOT PERMISSIONS`, check:
  - Send Messages
  - Read Messages/View Channels
  - Read Message History
- Copy the generated URL at the bottom
- Paste this URL into your Browser
- Select your Discord Server where the bot will be in
- Click `Authorize`

Go to **your .env File** again, and add this line:
```
TOKEN=TOKENTHATYOUCOPYED
```


## Execution

### Discord Bot

1. Run your discord bot directly (for testing):
```bash
`python bot/main.py`
```

2. Run as a systemd service (recommended):

- Create `/etc/systemd/system/discord-bot.service`
- Paste this into that file:

```ini
[Unit]
Description=Discord Update Bot
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/PATH/TO/BOT
ExecStart=/usr/bin/python3 /PATH/TO/BOT/main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

- Run the following commands:
```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
```

- Test it: run `!update all now` in your Discord Server

The bot will now run in the background and start on system startup! To disable it, run `sudo systemctl stop discord-bot`.
To delete the systemd service, delete the `/etc/systemd/system/discord-bot.service` file

### Webhook Handler

1. Run the Handler directly (for testing):
`pip install flask requests python-dotenv && python webhook_handler.py`

2. Run as a systemd service (recommended):
- Create `/etc/systemd/system/webhook-handler.service`
- Paste this into that file:

```ini
[Unit]
Description=Update Webhook Handler
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/PATH/TO/PYTHON/FILE
ExecStart=/usr/bin/python3 /PATH/TO/PYTHON/FILE/webhook_handler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

- Run the following commands:
```bash
sudo systemctl daemon-reload
sudo systemctl enable webhook-handler
sudo systemctl start webhook-handler
```


The Webhook Handler will now run in the background and start on system startup! To disable it, run `sudo systemctl stop webhook-handler`.
To delete the systemd service, delete the `/etc/systemd/system/webhook-handler.service` file
