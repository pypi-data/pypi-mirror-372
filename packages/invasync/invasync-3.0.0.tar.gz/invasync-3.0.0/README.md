# InvaSync

Synchronize your [flashed invaders](https://www.space-invaders.com/flashinvaders) to your [MySpaceInvaderMap](https://invaders.code-rhapsodie.com) easily!

## Installation

```sh
uv tool install invasync
```

## Usage

1. Create a `users.json` file:

```json
[
  {
    "name": "YOUR NAME",
    "flash_uid": "YOUR FLASH UID",
    "map_email": "YOUR INVADER MAP EMAIL",
    "map_password": "YOUR INVADER MAP PASSWORD",
    "map_token": "leave empty"
  },
  ...
]
```

2. Run InvaSync:

```sh
invasync -u users.json
```

3. Enjoy!

## Automatic updates

The following code will schedule a cron job running every 10 minutes:

```crontab
*/10 * * * * /home/USER/.local/bin/invasync -u /path/to/user.json
```
