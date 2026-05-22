from pathlib import Path

import requests


USERNAME = "MonsieurNam"
THEME = "tokyonight"
OUTPUT_FILE = Path("cards/stats.svg")


def fetch_profile_summary_card(username: str = USERNAME, theme: str = THEME) -> str:
    url = (
        "https://github-profile-summary-cards.vercel.app/api/cards/"
        f"profile-details?username={username}&theme={theme}"
    )
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    if "<svg" not in response.text:
        raise ValueError("Profile summary API did not return SVG content")

    return response.text


def write_card(svg_content: str, output_file: Path = OUTPUT_FILE) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(svg_content, encoding="utf-8")


if __name__ == "__main__":
    svg = fetch_profile_summary_card()
    write_card(svg)
    print(f"SVG file created: {OUTPUT_FILE}")
