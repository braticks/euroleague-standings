# EuroLeague Standings for Home Assistant

Custom Home Assistant integration that exposes the current EuroLeague standings as a sensor for Lovelace cards.

## Features

- Automatic current EuroLeague season detection
- Automatic current regular-season round detection
- Standings from the EuroLeague public API
- Team logos from EuroLeague club data
- Points for, points against and points differential calculated from played regular-season games
- One sensor: `sensor.euroleague_standings`
- HACS compatible

The sensor attributes contain the season, current round and a `teams` list with position, team code, name, logo, games played, wins, losses, `points_for`, `points_against` and `points_diff`.

## Install with HACS

1. HACS → Integrations → three dots → Custom repositories.
2. Add `https://github.com/braticks/euroleague-standings` as **Integration**.
3. Install **EuroLeague Standings**.
4. Restart Home Assistant.
5. Settings → Devices & services → Add integration → **EuroLeague Standings**.

## Data source

This project uses public EuroLeague API endpoints and is not affiliated with EuroLeague Basketball.

EuroLeague name and logo are trademarks of their respective owner.
