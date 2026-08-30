name: Run Real Estate Intelligence Agent

on:
  schedule:
    - cron: '0 */6 * * *'
  workflow_dispatch:

permissions:
  contents: write

jobs:
  run-agent:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Setup Python
        uses: setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: pip install requests

      - name: Run Real Estate Intelligence Agent
        env:
          RAPIDAPI_KEY: ${{ secrets.RAPIDAPI_KEY }}
        run: python agent.py

      - name: Commit and Push Changes
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git add properties.json
          git diff --quiet && git diff --staged --quiet || (git commit -m "Auto-update live properties via RapidAPI [skip ci]" && git push)
