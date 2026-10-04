# EuroLeague Standings for Home Assistant

One HACS integration for EuroLeague standings **and** the Lovelace card.

## Features

- Automatic current EuroLeague season detection
- Automatic current regular-season round detection
- Standings from the EuroLeague public API
- Team logos from EuroLeague club data
- Points for, points against and point differential calculated from played regular-season games
- Sensor: `sensor.euroleague_standings`
- Bundled `custom:euroleague-standings-card`
- Automatic Lovelace resource registration in storage mode
- Visual card editor in English
- Configurable TOP N, favorite team, Playoff / Play-In zones, team-logo mode, header mode, GP and +/- columns
- HACS compatible

## Installation with HACS

1. HACS → Integrations → three dots → Custom repositories.
2. Add `https://github.com/braticks/euroleague-standings` as **Integration**.
3. Install **EuroLeague Standings**.
4. Restart Home Assistant.
5. Settings → Devices & services → Add integration → **EuroLeague Standings**.
6. Add **EuroLeague Standings Card** from the dashboard card picker.

No separate HACS Dashboard repository is required from version 1.2.0 onward.

If the old `euroleague-standings-card` Dashboard repository was previously installed, update this integration first, restart Home Assistant, verify the card works, then the separate Dashboard repository can be removed from HACS.

### Manual YAML example

```yaml
type: custom:euroleague-standings-card
entity: sensor.euroleague_standings
count: 10
favorite_team: ZAL
always_show_favorite: true
team_logo_mode: background
header_style: logo
show_round: true
show_gp: false
show_diff: true
show_zones: true
compact: false
highlight_favorite: true
```

## Lovelace YAML resource mode

The integration registers the card automatically when Lovelace resources use storage mode. If resources are managed in YAML, add this module manually:

```yaml
url: /euroleague_standings/euroleague-standings-card.js
resource_type: module
```

## Sensor data

The `teams` attribute contains position, team code, name, logo, games played, wins, losses, `points_for`, `points_against` and `points_diff`.

## Data source

This project uses public EuroLeague API endpoints and is not affiliated with EuroLeague Basketball.

EuroLeague name and logo are trademarks of their respective owner.
