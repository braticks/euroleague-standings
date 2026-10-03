"""Data coordinator for EuroLeague Standings."""

from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import EuroLeagueApi, EuroLeagueApiError
from .const import DEFAULT_UPDATE_INTERVAL, NAME

_LOGGER = logging.getLogger(__name__)


class EuroLeagueStandingsCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinate EuroLeague standings updates."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.api = EuroLeagueApi(async_get_clientsession(hass))
        super().__init__(
            hass,
            _LOGGER,
            name=NAME,
            update_interval=DEFAULT_UPDATE_INTERVAL,
        )

    async def _async_update_data(self) -> dict[str, Any]:
        season = _current_season()

        try:
            rounds = await self.api.async_get_rounds(season)
            round_info = _select_regular_season_round(rounds)
            round_number = _as_int(round_info.get("round"))
            if round_number is None:
                raise EuroLeagueApiError("Could not determine the current round")

            standings = await self.api.async_get_standings(season, round_number)
            clubs = await self.api.async_get_clubs(season)
        except EuroLeagueApiError as err:
            raise UpdateFailed(str(err)) from err

        clubs_by_code = {
            str(club.get("code", "")).upper(): club
            for club in clubs
            if club.get("code")
        }

        teams = [_normalise_team(row, clubs_by_code) for row in standings]
        teams = [team for team in teams if team["position"] is not None]
        teams.sort(key=lambda team: team["position"])

        return {
            "season": season,
            "season_code": f"E{season}",
            "round": round_number,
            "round_name": round_info.get("name") or f"Round {round_number}",
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "team_count": len(teams),
            "teams": teams,
        }


def _current_season() -> int:
    now = datetime.now(timezone.utc)
    return now.year if now.month >= 7 else now.year - 1


def _select_regular_season_round(rounds: list[dict[str, Any]]) -> dict[str, Any]:
    regular = [
        item
        for item in rounds
        if str(item.get("phaseTypeCode", "")).upper()
        in {"RS", "REG", "REGULAR SEASON"}
    ]
    candidates = regular or rounds
    if not candidates:
        raise EuroLeagueApiError("EuroLeague API returned no rounds")

    now = datetime.now(timezone.utc)
    started: list[tuple[datetime, dict[str, Any]]] = []

    for item in candidates:
        start = _parse_datetime(item.get("minGameStartDate"))
        if start is not None and start <= now:
            started.append((start, item))

    if started:
        started.sort(key=lambda value: value[0])
        return started[-1][1]

    return min(
        candidates,
        key=lambda item: _as_int(item.get("round")) or 9999,
    )


def _parse_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalise_team(
    row: dict[str, Any], clubs_by_code: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    code = str(
        _first(
            row,
            "club.code",
            "clubCode",
            "ClubCode",
            "teamCode",
            "TeamCode",
            "code",
        )
        or ""
    ).upper()

    club = clubs_by_code.get(code, {})

    row_images = _first(row, "club.images")
    if not isinstance(row_images, dict):
        row_images = {}

    club_images = club.get("images") if isinstance(club.get("images"), dict) else {}

    name = (
        _first(
            row,
            "club.name",
            "clubName",
            "ClubName",
            "teamName",
            "TeamName",
            "name",
        )
        or club.get("name")
        or code
    )

    logo = row_images.get("crest") or club_images.get("crest")

    return {
        "position": _as_int(_first(row, "position", "Position")),
        "code": code,
        "name": str(name),
        "logo": logo,
        "games_played": _as_int(_first(row, "gamesPlayed", "GamesPlayed", "played")) or 0,
        "wins": _as_int(_first(row, "gamesWon", "GamesWon", "wins", "won")) or 0,
        "losses": _as_int(_first(row, "gamesLost", "GamesLost", "losses", "lost")) or 0,
    }


def _first(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = _get_value(row, key)
        if value is not None:
            return value
    return None


def _get_value(row: dict[str, Any], key: str) -> Any:
    """Read either a literal key or a dotted path from an API row."""
    if key in row:
        return row[key]

    current: Any = row
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _as_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
