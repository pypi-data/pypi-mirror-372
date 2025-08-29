# FPL-data-loader
Python package for loading and transforming data from the Fantasy Premier Leage API.

## Usage

### `fpl_data_loader.load`
For getting raw data in JSON form, use the `fpl_data_loader.load` module.

This module provides a single class: `FplApiDataRaw`

This class can be used to download all relevant data from the FPL API, including:
  * Elements (Players)
  * Element types (Positions)
  * Teams
  * Events (Game weeks)
  * Fixtures

To use the `FplApiDataRaw` class, first create an instance of the class:
```python
from fpl_data.load import FplApiDataRaw

# make a request to the FPL API
data = FplApiDataRaw()
```

Then, you can access the data using the following attributes:
  * `elements_json`: A list of all players in the current season
  * `element_types_json`: A list of all positions in the FPL game
  * `teams_json`: A list of all teams in the Premier League
  * `events_json`: A list of all game weeks in the current season
  * `fixtures_json`: A list of all fixtures in the current season

For example, to get the list of all players in the current season, you would do the following:
```python
players = data.elements_json
```

The `get_element_summary` function can be used to get all past gameweek/season info for a given player_id.

To use the `get_element_summary` function, you need to pass the `player_id` as an argument:
```python
from fpl_data.load import get_element_summary


summary = get_element_summary(player_id)
```

The `summary` object will contain the following information:
  * `history`: all gameweek data for the current season
  * `history_past`: all summary data for past seasons
  * `fixtures`: all upcoming fixtures in current season

For example, to get all past gameweek/season info for the player with ID 1, you would do the following:
```python
summary = get_element_summary(1)
```

The `history` attribute of the summary object will contain a list of dictionaries, each of which representing a gameweek. The dictionaries will contain the following keys:
  * `gameweek`: The gameweek number.
  * `points`: The number of points the player scored in the gameweek.
  * `minutes`: The number of minutes the player played in the gameweek.
  * `goals_scored`: The number of goals the player scored in the gameweek.
  * `assists`: The number of assists the player provided in the gameweek.
  * `clean_sheets`: The number of clean sheets the player kept in the gameweek.
  * `bonus`: The bonus points the player earned in the gameweek.
  * `red_card`: A boolean value indicating whether the player was sent off in the gameweek.

The `history_past` attribute of the summary object will contain a list of dictionaries, each of which representing a summary from a past season.

### `fpl_data.transform`
For getting enriched data as Pandas DataFrames, use the `fpl_data.transform` module.

This module builds on the `load` module, by performing some transformations including:
  - Renaming columns to match those shown in the FPL website
  - Correcting data types for some columns
  - Calculating additional columns such as:
    - `GI` (goal involvements): goals plus assists
    - `Pts90`: points scored per 90 minutes

The `FplApiDataTransformed` class can be used to download and transform data from the FPL API, which are then returned as Pandas DataFrames:
  * `players_df`: summary of players' season statistics so far
  * `positions_df`: all positions in the FPL game
  * `teams_df`: summary of teams in the Premier League
  * `gameweeks_df`: list of all game weeks in the current season

To use the `FplApiDataTransformed` class, first create an instance of the class:
```python
from fpl_data.transform import FplApiDataTransformed

# load and transform data
data = FplApiDataTransformed()
```

Then, you can access the data in DataFrame format using the classes attributes.

For example, to get the main players dataframe, you would do the following:
```python
players = data.players_df
```

---
## Installation

### Using pip (recommended for users)
```bash
pip install FPL-data-loader
```

### Using [UV](https://docs.astral.sh/uv/) (recommended for development)
```bash
uv add FPL-data-loader
```

---
## Local development
If you would like to contribute to this package, you can set up a development environment using [UV](https://docs.astral.sh/uv/):

### 1. Clone the repository
```bash
git clone https://github.com/James-Leslie/fpl-data
cd fpl-data
```

### 2. Install dependencies
```bash
uv sync
```

### 3. Run quality checks
```bash
uv run ruff format   # Format code
uv run ruff check    # Lint code
uv run mypy src/     # Type checking
uv run pytest       # Run tests
```

### 4. Create a pull request
