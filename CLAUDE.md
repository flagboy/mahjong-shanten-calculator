# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Mahjong Shanten calculation simulation project that uses the `mahjong` Python library to analyze hand configurations and their distances from winning.

## Key Dependencies

- `mahjong` library for Shanten calculations and tile conversion
- Requires `from mahjong.shanten import Shanten` and `from mahjong.tile import TilesConverter`

## Code Architecture

The main script (`shanten.py`) performs Monte Carlo simulation:
- Generates random Mahjong hands with specific constraints
- Uses tile filtering to avoid invalid configurations
- Calculates Shanten values (distance to winning) for each hand
- Collects statistical distribution of results

## Running the Code

```bash
python shanten.py
```

The script runs 100,000 iterations and outputs a distribution of Shanten values.