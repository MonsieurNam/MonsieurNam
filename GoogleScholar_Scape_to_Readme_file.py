from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

import requests
from bs4 import BeautifulSoup


SCHOLAR_URL = "https://scholar.google.com/citations?user=OtccK6UAAAAJ&hl=en&pagesize=100"
README_FILE = Path("README.md")
START_MARKER = "<!-- SCHOLAR-LIST:START -->"
END_MARKER = "<!-- SCHOLAR-LIST:END -->"

PAPER_QUALITY: dict[str, dict[str, str]] = {
    "engineering science and technology, an international journal": {
        "quality": "Q1",
        "rank": "SJR 2025: 0.957",
        "source": "SCImago",
        "source_url": "https://www.scimagojr.com/journalsearch.php?q=21100806003&tip=sid",
    },
    "signal, image and video processing": {
        "quality": "Q2",
        "rank": "SJR 2025: 0.561",
        "source": "SCImago",
        "source_url": "https://www.scimagojr.com/journalsearch.php?q=6200180165&tip=sid",
    },
    "multimedia tools and applications": {
        "quality": "Q1",
        "rank": "SJR 2025: 0.798",
        "source": "SCImago",
        "source_url": "https://www.scimagojr.com/journalsearch.php?q=25627&tip=sid",
    },
    "international conference on computational science and its applications": {
        "quality": "Conference",
        "rank": "CORE C",
        "source": "CORE",
        "source_url": "https://portal.core.edu.au/conf-ranks/953/",
    },
    "asian conference on intelligent information and database systems": {
        "quality": "Conference",
        "rank": "CORE B",
        "source": "ACIIDS / CORE",
        "source_url": "https://aciids.pwr.edu.pl/2023/",
    },
}


def normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def get_text(tag: Any, default: str = "") -> str:
    if tag is None:
        return default
    return tag.get_text(" ", strip=True)


def fetch_scholar_html(url: str = SCHOLAR_URL) -> str:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()
    return response.text


def extract_metrics(soup: BeautifulSoup) -> dict[str, str]:
    labels = {
        "citations": "citations",
        "h-index": "h_index",
        "i10-index": "i10_index",
    }
    metrics = {value: "0" for value in labels.values()}

    for row in soup.select("#gsc_rsb_st tr"):
        label = normalize_text(get_text(row.select_one(".gsc_rsb_sc1 a")))
        values = row.select(".gsc_rsb_std")
        if label in labels and values:
            metrics[labels[label]] = get_text(values[0], "0") or "0"

    return metrics


def quality_for_venue(venue: str) -> dict[str, str]:
    normalized_venue = normalize_text(venue)
    for fragment, metadata in PAPER_QUALITY.items():
        if fragment in normalized_venue:
            return metadata

    return {
        "quality": "-",
        "rank": "-",
        "source": "Manual review needed",
        "source_url": "",
    }


def parse_scholar_profile(html: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    papers = []

    for entry in soup.select("tr.gsc_a_tr"):
        title_tag = entry.select_one("a.gsc_a_at")
        detail_rows = entry.select("div.gs_gray")
        citation_tag = entry.select_one("a.gsc_a_ac") or entry.select_one(".gsc_a_ac")
        year_tag = entry.select_one(".gsc_a_h")
        venue = get_text(detail_rows[1]) if len(detail_rows) > 1 else ""
        quality = quality_for_venue(venue)

        paper = {
            "Title": get_text(title_tag, "No title"),
            "URL": (
                "https://scholar.google.com" + title_tag["href"]
                if title_tag and title_tag.has_attr("href")
                else ""
            ),
            "Authors": get_text(detail_rows[0], "Unknown") if detail_rows else "Unknown",
            "Venue": venue or "Unknown",
            "Citations": get_text(citation_tag, "0") or "0",
            "Year": get_text(year_tag, "N/A") or "N/A",
            "Quality": quality["quality"],
            "Rank": quality["rank"],
            "Source": quality["source"],
            "SourceURL": quality["source_url"],
        }
        papers.append(paper)

    return {
        "name": get_text(soup.select_one("#gsc_prf_in"), "Google Scholar"),
        "metrics": extract_metrics(soup),
        "papers": papers,
    }


def render_source_link(paper: dict[str, str]) -> str:
    source = escape(paper["Source"])
    source_url = paper.get("SourceURL", "")
    if not source_url:
        return source
    return f'<a href="{escape(source_url, quote=True)}">{source}</a>'


def render_scholar_section(profile: dict[str, Any], updated_at: str | None = None) -> str:
    metrics = profile["metrics"]

    html_content = "\n\n"
    html_content += '<p align="center">\n'
    html_content += f'  <strong>Citations:</strong> {escape(metrics["citations"])} &nbsp;|&nbsp;\n'
    html_content += f'  <strong>h-index:</strong> {escape(metrics["h_index"])} &nbsp;|&nbsp;\n'
    html_content += f'  <strong>i10-index:</strong> {escape(metrics["i10_index"])}\n'
    html_content += "</p>\n\n"
    html_content += '<table id="scholar-table">\n'
    html_content += "  <tr>\n"
    html_content += "    <th>Title</th>\n"
    html_content += "    <th>Venue</th>\n"
    html_content += "    <th>Citations</th>\n"
    html_content += "    <th>Quality / Rank</th>\n"
    html_content += "    <th>Source</th>\n"
    html_content += "    <th>Year</th>\n"
    html_content += "  </tr>\n"

    for paper in profile["papers"]:
        title = escape(paper["Title"])
        url = escape(paper["URL"], quote=True)
        title_cell = f'<a href="{url}">{title}</a>' if url else title
        quality_rank = f'{escape(paper["Quality"])} / {escape(paper["Rank"])}'
        html_content += "  <tr>\n"
        html_content += f"    <td>{title_cell}</td>\n"
        html_content += f'    <td>{escape(paper["Venue"])}</td>\n'
        html_content += f'    <td align="center">{escape(paper["Citations"])}</td>\n'
        html_content += f"    <td>{quality_rank}</td>\n"
        html_content += f"    <td>{render_source_link(paper)}</td>\n"
        html_content += f'    <td align="center">{escape(paper["Year"])}</td>\n'
        html_content += "  </tr>\n"

    html_content += "</table>\n\n"
    sync_note = (
        f": {escape(updated_at)}"
        if updated_at
        else ". Automated weekly sync is enabled"
    )
    html_content += (
        f'<p><em>Last synced from <a href="{escape(SCHOLAR_URL, quote=True)}">'
        f"Google Scholar</a>{sync_note}.</em></p>\n"
    )

    return html_content


def update_readme(section: str, readme_file: Path = README_FILE) -> None:
    readme_content = readme_file.read_text(encoding="utf-8")
    start_pos = readme_content.find(START_MARKER)
    end_pos = readme_content.find(END_MARKER)

    if start_pos == -1 or end_pos == -1 or start_pos >= end_pos:
        raise ValueError("Scholar markers were not found in README.md")

    start_pos += len(START_MARKER)
    new_readme_content = readme_content[:start_pos] + section + readme_content[end_pos:]
    readme_file.write_text(new_readme_content, encoding="utf-8")


def main() -> None:
    html = fetch_scholar_html()
    profile = parse_scholar_profile(html)
    update_readme(render_scholar_section(profile))


if __name__ == "__main__":
    main()
