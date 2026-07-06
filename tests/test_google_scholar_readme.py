import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from GoogleScholar_Scape_to_Readme_file import (
    PAPER_QUALITY,
    parse_scholar_profile,
    render_scholar_section,
)


SCHOLAR_HTML = """
<html>
  <div id="gsc_prf_in">Nguyen Ngo Nhat Nam</div>
  <table id="gsc_rsb_st">
    <tr><td class="gsc_rsb_sc1"><a>Citations</a></td><td class="gsc_rsb_std">16</td><td class="gsc_rsb_std">16</td></tr>
    <tr><td class="gsc_rsb_sc1"><a>h-index</a></td><td class="gsc_rsb_std">3</td><td class="gsc_rsb_std">3</td></tr>
    <tr><td class="gsc_rsb_sc1"><a>i10-index</a></td><td class="gsc_rsb_std">0</td><td class="gsc_rsb_std">0</td></tr>
  </table>
  <tr class="gsc_a_tr">
    <td class="gsc_a_t">
      <a class="gsc_a_at" href="/citations?view_op=view_citation&amp;citation_for_view=abc">
        Grounding DINO and distillation-enhanced model for advanced traffic sign detection and classification in autonomous vehicles
      </a>
      <div class="gs_gray">HN Tran, NNN Nguyen, NQP Le</div>
      <div class="gs_gray">Engineering Science and Technology, an International Journal 64, 102028, 2025</div>
    </td>
    <td class="gsc_a_c"><a class="gsc_a_ac gs_ibl">7</a></td>
    <td class="gsc_a_y"><span class="gsc_a_h gsc_a_hc gs_ibl">2025</span></td>
  </tr>
</html>
"""


def test_parse_scholar_profile_reads_metrics_and_papers():
    profile = parse_scholar_profile(SCHOLAR_HTML)

    assert profile["metrics"] == {
        "citations": "16",
        "h_index": "3",
        "i10_index": "0",
    }
    assert profile["papers"][0]["Title"].startswith("Grounding DINO")
    assert profile["papers"][0]["Citations"] == "7"
    assert profile["papers"][0]["Quality"] == "Q1"
    assert profile["papers"][0]["Rank"] == "SJR 2025: 0.957"


def test_render_scholar_section_includes_metrics_quality_and_sources():
    profile = parse_scholar_profile(SCHOLAR_HTML)
    section = render_scholar_section(profile, updated_at="2026-07-06 00:00:00 UTC")

    assert "<strong>Citations:</strong> 16" in section
    assert "<strong>h-index:</strong> 3" in section
    assert "<th>Quality / Rank</th>" in section
    assert "Q1" in section
    assert PAPER_QUALITY["engineering science and technology, an international journal"]["source"] in section
