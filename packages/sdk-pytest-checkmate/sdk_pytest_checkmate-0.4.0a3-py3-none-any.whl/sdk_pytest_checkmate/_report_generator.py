"""HTML test report generation with timeline visualization and theme support."""

import datetime as _dt
import html
import json as _json
import pathlib as _pl
import re
from typing import Any


def escape_html(s: str) -> str:
    """Escape HTML special characters in a string.

    Args:
        s: String to escape.

    Returns:
        HTML-escaped string with quotes escaped.

    Example:
        >>> escape_html('<script>alert("test")</script>')
        '&lt;script&gt;alert(&quot;test&quot;)&lt;/script&gt;'
    """
    return html.escape(s, quote=True)


def format_timeline(
    steps: list[dict[str, Any]],
    soft: list[dict[str, Any]],
    data_reports: list[dict[str, Any]],
) -> str:
    """Format test timeline with steps, soft checks, and data reports in chronological order.

    Args:
        steps: List of step records with execution details.
        soft: List of soft assertion records.
        data_reports: List of data attachment records.

    Returns:
        HTML string representing the formatted timeline.

    Note:
        Records are ordered by their sequence number and grouped by step execution time.
    """
    seq: list[tuple[int, str, dict[str, Any]]] = []
    for s in steps:
        seq.append((s.get("seq", 0), "step", s))
    for sc in soft:
        seq.append((sc.get("seq", 0), "soft", sc))
    for dr in data_reports:
        seq.append((dr.get("seq", 0), "data", dr))
    if not seq:
        return ""
    seq.sort(key=lambda x: x[0])

    def fmt_duration(sd: dict[str, Any]) -> str:
        if "start" in sd and "end" in sd:
            try:
                d = sd["end"] - sd["start"]
                if d >= 0.001:
                    return f" ({d:.3f}s)"
            except Exception:
                return ""
        return ""

    def render_data(dr: dict[str, Any]) -> str:
        summary = escape_html(dr.get("label", "data"))
        payload = dr.get("payload")
        try:
            if isinstance(payload, dict | list):
                pretty = _json.dumps(payload, ensure_ascii=False, indent=2)
                details = f"<pre>{escape_html(pretty)}</pre>"
            else:
                details = f"<pre>{escape_html(str(payload))}</pre>"
        except Exception:
            details = f"<pre>{escape_html(str(payload))}</pre>"
        return (
            "<li class='data-item'>DATA: "
            f"<span class='data-summary'>{summary}</span>"
            f"<div class='data-details hidden'>{details}</div></li>"
        )

    def render_check(chk: dict[str, Any]) -> str:
        cls = "pass" if chk.get("passed") else "fail"
        icon = "✔" if chk.get("passed") else "✖"
        message = escape_html(chk.get("message", ""))
        details = chk.get("details")

        details_html = ""
        if details is not None:
            details_text = "\n".join(str(item) for item in details) if isinstance(details, list) else str(details)
            details_html = f"<div class='check-details hidden'><pre>{escape_html(details_text)}</pre></div>"

        has_details = "true" if details is not None else "false"

        return (
            "<ul class='checks'><li class='"
            + cls
            + "'>CHECK: <span class='check-summary' data-has-details='"
            + has_details
            + "'>"
            + icon
            + " "
            + message
            + "</span>"
            + details_html
            + "</li></ul>"
        )

    pre_items: list[str] = []
    pos = 0
    while pos < len(seq) and seq[pos][1] != "step":
        kind = seq[pos][1]
        obj = seq[pos][2]
        if kind == "soft":
            pre_items.append(render_check(obj))
        else:
            pre_items.append("<ul class='data-items'>" + render_data(obj) + "</ul>")
        pos += 1

    out: list[str] = ["<h4>Full details</h4>"]
    if pre_items:
        out.append("<div class='pre-checks'>" + "".join(pre_items) + "</div>")

    steps_markup: list[str] = []
    post_steps_items: list[str] = []

    step_ranges = []
    for _, kind, obj in seq[pos:]:
        if kind == "step":
            step_start = obj.get("start", 0)
            step_end = obj.get("end", float("inf"))
            step_ranges.append((step_start, step_end, obj))

    for step_start, step_end, step_obj in step_ranges:
        step_attachments = []

        for _, kind, obj in seq[pos:]:
            if kind != "step":
                element_time = obj.get("time", 0)
                if step_start <= element_time <= step_end:
                    if kind == "soft":
                        step_attachments.append(render_check(obj))
                    else:
                        step_attachments.append(
                            "<ul class='data-items'>" + render_data(obj) + "</ul>",
                        )

        steps_markup.append(
            "<li>STEP: "
            + escape_html(step_obj.get("name", ""))
            + fmt_duration(step_obj)
            + ""
            + "".join(step_attachments)
            + "</li>",
        )

    last_step_end = 0
    if step_ranges:
        last_step_end = max(step_end for _, step_end, _ in step_ranges)

    for _, kind, obj in seq[pos:]:
        if kind != "step":
            element_time = obj.get("time", 0)
            if element_time > last_step_end:
                if kind == "soft":
                    post_steps_items.append(render_check(obj))
                else:
                    post_steps_items.append(
                        "<ul class='data-items'>" + render_data(obj) + "</ul>",
                    )

    out.append("<ol class='steps'>" + "".join(steps_markup) + "</ol>")

    if post_steps_items:
        out.append("<div class='post-steps'>" + "".join(post_steps_items) + "</div>")
    return "".join(out)


def format_errors(r: dict[str, Any]) -> str:
    """Format error information for a test result into HTML.

    Args:
        r: Test result dictionary containing status, steps, and failure details.

    Returns:
        HTML string containing formatted error information or empty string if no errors.

    Note:
        Handles different error types including test failures, step errors, and soft assertion failures.
        Does not show errors block for SKIPPED, XFAIL, and XPASS statuses as they are not actual errors.
    """
    status = r.get("status")

    if status in {"SKIPPED", "XFAIL", "XPASS"}:
        return ""

    steps = r.get("steps", [])
    soft = r.get("soft_checks", [])
    failed_soft = [s for s in soft if not s.get("passed")]
    step_errors = [s for s in steps if s.get("error")]
    failure_text = r.get("full", "") if status in {"FAILED", "ERROR"} else ""
    parts: list[str] = []
    if failure_text:
        parts.append(f"<pre class='details'>{escape_html(failure_text)}</pre>")
    if step_errors:
        li = [
            f"<li><span class='step-error'>Step '{escape_html(s.get('name', ''))}': "
            f"{escape_html(str(s.get('error')))}</span></li>"
            for s in step_errors
        ]
        parts.append(
            "<ul style='margin:4px 0 8px 16px;padding:0;'>" + "".join(li) + "</ul>",
        )
    if failed_soft and not failure_text.startswith("Soft assertion failures"):
        li = [f"<li style='color:#c40000;font-weight:600;'>✖ {escape_html(s['message'])}</li>" for s in failed_soft]
        parts.append(
            "<ul style='margin:4px 0 8px 16px;padding:0;'>" + "".join(li) + "</ul>",
        )
    if not parts:
        return ""
    return "<div class='errors-block'><h4>Errors</h4>" + "".join(parts) + "</div>"


def compute_counts(sub: list[dict[str, Any]]) -> dict[str, int]:
    """Count test results by status.

    Args:
        sub: List of test result dictionaries.

    Returns:
        Dictionary mapping status strings to their counts.

    Example:
        >>> results = [{"status": "PASSED"}, {"status": "FAILED"}, {"status": "PASSED"}]
        >>> compute_counts(results)
        {"PASSED": 2, "FAILED": 1}
    """
    c: dict[str, int] = {}
    for r in sub:
        c[r["status"]] = c.get(r["status"], 0) + 1
    return c


def slugify(raw: str) -> str:
    """Convert string to URL-safe slug format.

    Args:
        raw: Raw string to convert.

    Returns:
        Lowercase string with spaces replaced by hyphens and special characters by underscores.

    Example:
        >>> slugify("My Test Epic!")
        "my-test-epic_"
    """
    raw = raw.strip().lower().replace(" ", "-")
    return re.sub(r"[^a-z0-9_-]", "_", raw) or "group"


def get_html_css() -> str:
    """Get the complete CSS stylesheet for HTML reports.

    Returns:
        CSS string with light and dark theme styles for test reports.

    Note:
        Includes responsive design, theme switching, and status-specific styling.
    """
    return """
    body { font-family: -apple-system, Arial, sans-serif; margin:0; padding:0 0 60px 0; background:#f6f8fa; }
    header { background:#e8f1ff; padding:14px 24px; font-size:20px; font-weight:600; text-align:center; overflow-wrap:break-word; word-wrap:break-word; }
    header .title { overflow-wrap:break-word; word-wrap:break-word; }
    .theme-toggle { cursor:pointer; border:1px solid #b4c7dd; background:#fff; color:#0a2a45; padding:6px 14px; border-radius:18px; font-size:13px; font-weight:500; box-shadow:0 1px 2px rgba(0,0,0,.12); transition:background .15s,border-color .15s; }
    .theme-toggle-floating { position:fixed; top:10px; right:14px; z-index:1100; }
    .theme-toggle:hover { background:#f0f6ff; }
    .summary { display:flex; gap:12px; flex-wrap:wrap; padding:12px 24px; justify-content:center; }
    .badge { border:1px solid #3332; border-radius:999px; padding:6px 14px; cursor:pointer; font-size:13px; background:#fff; overflow-wrap:break-word; word-wrap:break-word; }
    .badge[data-status="PASSED"] { background:#d4f7d9; }
    .badge[data-status="FAILED"] { background:#ffd8d6; }
    .badge[data-status="ERROR"] { background:#ffe1b3; }
    .badge[data-status="SKIPPED"] { background:#fff5cc; }
    .badge[data-status="XFAIL"], .badge[data-status="XPASS"] { background:#e6dcff; }
    table { border-collapse:collapse; width:100%; background:#fff; table-layout:fixed; }
    th, td { border:1px solid #d0d7de; padding:6px 8px; font-size:13px; vertical-align:top; overflow-wrap:break-word; word-wrap:break-word; }
    th { background:#f0f6ff; text-align:left; }
    th:nth-child(1), td:nth-child(1) { width:35%; } /* Test column */
    th:nth-child(2), td:nth-child(2) { width:10%; } /* Status column */
    th:nth-child(3), td:nth-child(3) { width:12%; } /* Duration column */
    th:nth-child(4), td:nth-child(4) { width:43%; } /* Details column */
    pre { white-space:pre-wrap; overflow-wrap:anywhere; word-break:break-word; max-width:100%; box-sizing:border-box; }
    .details { white-space:pre-wrap; font-family:Menlo, monospace; max-width:100%; max-height:240px; overflow:auto; word-wrap:break-word; overflow-wrap:anywhere; }
    tr.status-PASSED td.details { color:#1a7f37; }
    tr.status-FAILED td.details { color:#b30000; }
    tr.status-ERROR td.details { color:#c85500; }
    tr.status-SKIPPED td.details { color:#8a6d00; }
    tr.status-XFAIL td.details, tr.status-XPASS td.details { color:#6941c6; }
    .steps { margin:4px 0 0 0; padding:0 0 0 28px; list-style:decimal; overflow-wrap:break-word; word-wrap:break-word; }
    .checks { list-style:none; margin:4px 0 4px 0; padding-left:28px; overflow-wrap:break-word; word-wrap:break-word; }
    .checks li { font-size:12px; overflow-wrap:break-word; word-wrap:break-word; }
    .data-items { list-style:none; margin:2px 0 2px 0; padding-left:24px; }
    .data-items .data-item { list-style:none; }
    .checks li.fail { color:#c40000; font-weight:600; }
    .checks li.pass { color:#1a7f37; }
    .check-summary[data-has-details="true"] { cursor:pointer; text-decoration:underline; }
    .check-details { margin-top:4px; overflow-wrap:break-word; word-wrap:break-word; }
    .check-details pre { white-space:pre-wrap; overflow-wrap:anywhere; word-break:break-word; max-width:100%; box-sizing:border-box; }
    .step-error { color:#c40000; font-weight:600; overflow-wrap:break-word; word-wrap:break-word; }
    .data-item { margin:4px 0; overflow-wrap:break-word; word-wrap:break-word; }
    .data-item .data-summary { cursor:pointer; font-weight:500; color:#0366d6; overflow-wrap:break-word; word-wrap:break-word; }
    .data-item .data-summary::before { content:'▶'; display:inline-block; margin-right:4px; transition:transform .18s ease; }
    .data-item.expanded .data-summary::before { transform:rotate(90deg); }
    .data-item .data-details { margin:4px 0 0 18px; overflow-wrap:break-word; word-wrap:break-word; }
    .data-item .data-details pre {
        max-width:100%;
        box-sizing:border-box;
        padding:8px 10px;
        margin:4px 0;
        border:1px solid #d0d7de;
        background:#f6f8fa;
        border-radius:4px;
        font-size:12px;
        line-height:1.4;
        white-space:pre-wrap;
        word-break:break-word;
        overflow-x:auto;
        overflow-y:auto;
        max-height:340px;
    }
    .data-item .data-details pre { overflow-wrap:anywhere; }
    .errors-block { border:1px solid #e99; background:#ffecec; padding:8px 12px; margin-top:12px; border-radius:4px; overflow-wrap:break-word; word-wrap:break-word; }
    .errors-block h4 { margin:0 0 6px 0; color:#b30000; }
    .errors-block pre { white-space:pre-wrap; overflow-wrap:anywhere; word-break:break-word; max-width:100%; box-sizing:border-box; }
    footer { position:fixed; bottom:0; left:0; right:0; background:#e8f1ff; padding:8px 16px; font-size:12px; color:#555; text-align:center; border-top:1px solid #d0d7de; }
    .hidden { display:none; }
    tr.main-row { cursor:pointer; }
    tr.detail-row td { background:#f3f6f9; }
    .detail-card { background:#fff; border:1px solid #d0d7de; border-left:6px solid #888; padding:10px 16px 14px 16px; border-radius:6px; max-width:100%; width:100%; box-sizing:border-box; margin:6px auto; box-shadow:0 2px 4px -2px rgba(0,0,0,0.12); overflow-wrap:break-word; word-wrap:break-word; }
    .detail-card.status-PASSED { border-left-color:#1a7f37; }
    .detail-card.status-FAILED { border-left-color:#b30000; }
    .detail-card.status-ERROR { border-left-color:#c85500; }
    .detail-card.status-SKIPPED { border-left-color:#8a6d00; }
    .detail-card.status-XFAIL { border-left-color:#6941c6; }
    .detail-card.status-XPASS { border-left-color:#6941c6; }
    .detail-card h4 { margin-top:14px; }
    .run-info { max-width:960px; margin:8px auto 4px; padding:6px 16px 10px; font-size:12px; color:#444; display:flex; flex-wrap:wrap; gap:18px; justify-content:center; }
    .run-info div { white-space:nowrap; }
    .test-stats { max-width:960px; margin:4px auto 12px; padding:6px 16px 10px; font-size:12px; color:#444; display:flex; flex-wrap:wrap; gap:18px; justify-content:center; }
    .test-stats div { white-space:nowrap; }
    td.status-cell { font-weight:600; }
    td.status-cell .st-PASSED { color:#1a7f37; }
    td.status-cell .st-FAILED { color:#b30000; }
    td.status-cell .st-ERROR { color:#c85500; }
    td.status-cell .st-SKIPPED { color:#8a6d00; }
    td.status-cell .st-XFAIL { color:#6941c6; }
    td.status-cell .st-XPASS { color:#6941c6; }

    .collapsible > .toggle { cursor:pointer; position:relative; user-select:none; }
    .collapsible > .toggle::before { content:'▶'; display:inline-block; margin-right:6px; transition:transform .18s ease; color:#555; }
    .collapsible.expanded > .toggle::before { transform:rotate(90deg); }
    .group-body, .story-body { padding:0 4px 4px; }
    .story-block { margin:10px auto 18px; max-width:1280px; background:#0000; }
    .story-block > .toggle { font-weight:600; }
    .story-block table { margin-top:2px; }
    .group-section { max-width:1280px; margin:0 auto; }
    /* Epic & Story heading sizing/alignment */
    .group-section h2.toggle { font-size:20px !important; text-align:left !important; padding:0 24px; }
    .story-block h3.toggle { font-size:18px !important; text-align:left !important; padding:0 28px; }

    /* ---------------- DARK THEME (activated via body.theme-dark) ---------------- */
    body.theme-dark { background:#1f2530; color:#d8dee6; }
    body.theme-dark header { background:#263040; color:#fff; overflow-wrap:break-word; word-wrap:break-word; }
    body.theme-dark .theme-toggle { background:#324054; border-color:#44556b; color:#e2ecf5; }
    body.theme-dark .theme-toggle:hover { background:#3a4b60; }
    body.theme-dark table { background:#27313f; }
    body.theme-dark th { background:#324054; color:#dfe6ee; }
    body.theme-dark th, body.theme-dark td { border-color:#425264; }
    body.theme-dark th:nth-child(1), body.theme-dark td:nth-child(1) { width:35%; } /* Test column */
    body.theme-dark th:nth-child(2), body.theme-dark td:nth-child(2) { width:10%; } /* Status column */
    body.theme-dark th:nth-child(3), body.theme-dark td:nth-child(3) { width:12%; } /* Duration column */
    body.theme-dark th:nth-child(4), body.theme-dark td:nth-child(4) { width:43%; } /* Details column */
    /* Dark theme: color the Details column by status, matching status badge colors */
    body.theme-dark tr.status-PASSED td.details { color:#61d088; }
    body.theme-dark tr.status-FAILED td.details { color:#ff8d87; }
    body.theme-dark tr.status-ERROR td.details { color:#ffb067; }
    body.theme-dark tr.status-SKIPPED td.details { color:#e7d47a; }
    body.theme-dark tr.status-XFAIL td.details, body.theme-dark tr.status-XPASS td.details { color:#b7a4ff; }
    body.theme-dark .detail-row td { background:#2e3947; }
    body.theme-dark .detail-card { background:#27313f; border-color:#425264; box-shadow:0 2px 4px -2px rgba(0,0,0,.55); overflow-wrap:break-word; word-wrap:break-word; }
    body.theme-dark .errors-block { background:#3d2225; border-color:#a04444; overflow-wrap:break-word; word-wrap:break-word; }
    body.theme-dark .errors-block pre { overflow-wrap:anywhere; word-break:break-word; }
    body.theme-dark .check-details pre { overflow-wrap:anywhere; word-break:break-word; }
    body.theme-dark footer { background:#263040; color:#b9c3cf; border-top-color:#425264; }
    body.theme-dark .badge { background:#324054; border-color:#4a5b6e; color:#d8dee6; overflow-wrap:break-word; word-wrap:break-word; }
    body.theme-dark .badge[data-status="PASSED"] { background:#1f5a2c; color:#d9f6e0; }
    body.theme-dark .badge[data-status="FAILED"] { background:#6a2320; color:#ffd9d8; }
    body.theme-dark .badge[data-status="ERROR"] { background:#744417; color:#ffe0c2; }
    body.theme-dark .badge[data-status="SKIPPED"] { background:#625815; color:#fff0b4; }
    body.theme-dark .badge[data-status="XFAIL"], body.theme-dark .badge[data-status="XPASS"] { background:#483a6d; color:#e6dcff; }
    body.theme-dark a, body.theme-dark .data-item .data-summary { color:#5aa9ff; }
    body.theme-dark .data-item .data-details pre { background:#1f2530; border-color:#425264; }
    body.theme-dark .run-info { color:#b9c3cf; }
    body.theme-dark .test-stats { color:#b9c3cf; }
    body.theme-dark .story-block h3.toggle, body.theme-dark .group-section h2.toggle { color:#d8dee6; }
    body.theme-dark .checks li.fail { color:#ffa8a4; }
    body.theme-dark .checks li.pass { color:#7dd9a0; }
    body.theme-dark .step-error { color:#ff9c96; }
    body.theme-dark .summary { background:#0000; }
    body.theme-dark .data-item .data-summary::before { color:#b9c3cf; }
    body.theme-dark .collapsible > .toggle::before { color:#b9c3cf; }
    body.theme-dark ::selection { background:#3b5169; color:#fff; }
    body.theme-dark .detail-card.status-PASSED { border-left-color:#2e8b57; }
    body.theme-dark .detail-card.status-FAILED { border-left-color:#d66560; }
    body.theme-dark .detail-card.status-ERROR { border-left-color:#d28a3a; }
    body.theme-dark .detail-card.status-SKIPPED { border-left-color:#c4a437; }
    body.theme-dark .detail-card.status-XFAIL, body.theme-dark .detail-card.status-XPASS { border-left-color:#8d79d6; }
    body.theme-dark .data-item .data-details pre { color:#d8dee6; }
    body.theme-dark .errors-block h4 { color:#ffc5c2; }
    body.theme-dark .st-PASSED { color:#61d088; }
    body.theme-dark .st-FAILED { color:#ff8d87; }
    body.theme-dark .st-ERROR { color:#ffb067; }
    body.theme-dark .st-SKIPPED { color:#e7d47a; }
    body.theme-dark .st-XFAIL, body.theme-dark .st-XPASS { color:#b7a4ff; }
    /* Ensure badges remain clickable with good contrast */
    body.theme-dark .badge:hover { filter:brightness(1.15); }
    """


def get_html_javascript() -> str:
    """Get the complete JavaScript code for HTML reports.

    Returns:
        JavaScript string with theme switching, filtering, and interactive functionality.

    Note:
        Handles theme persistence, test filtering by status, and collapsible sections.
    """
    return r"""
function applyStoredTheme(){
    // Default is dark; only switch to light if user explicitly saved 'light'
    try{ const t = localStorage.getItem('checkmateTheme'); if(t==='light'){ document.body.classList.remove('theme-dark'); } else { document.body.classList.add('theme-dark'); }}catch(e){}
    updateToggleLabel();
}
function toggleTheme(){
    document.body.classList.toggle('theme-dark');
    const isDark = document.body.classList.contains('theme-dark');
    try{ localStorage.setItem('checkmateTheme', isDark? 'dark':'light'); }catch(e){}
    updateToggleLabel();
}
function updateToggleLabel(){
    const btn = document.getElementById('themeToggle');
    if(!btn) return;
    const dark = document.body.classList.contains('theme-dark');
    btn.textContent = dark? 'Light theme' : 'Dark theme';
}
function filterStatusGroup(groupId, status) {
    const selector = 'tr.main-row[data-group="'+groupId+'"]';
    document.querySelectorAll(selector).forEach(tr=>{
        const idx = tr.dataset.idx;
        const detail = document.querySelector('tr.detail-row[data-idx="'+idx+'"]');
        const match = !status || tr.dataset.status===status;
        if(match){ tr.classList.remove('hidden'); if(detail) detail.classList.add('hidden'); }
        else { tr.classList.add('hidden'); if(detail) detail.classList.add('hidden'); }
    });
}

document.addEventListener('DOMContentLoaded', ()=>{
    applyStoredTheme();
    const toggleBtn = document.getElementById('themeToggle');
    if(toggleBtn){ toggleBtn.addEventListener('click', toggleTheme); }
    document.querySelectorAll('.summary').forEach(sumEl=>{
        const groupId = sumEl.getAttribute('data-group');
        if(!groupId) return;
        sumEl.querySelectorAll('.badge').forEach(b=>{
            b.addEventListener('click', ()=>{
                const st = b.dataset.status === 'ALL'? null : b.dataset.status;
                filterStatusGroup(groupId, st);
            });
        });
    });

    document.querySelectorAll('tr.main-row').forEach(row=>{
        row.addEventListener('click',()=>{
            const idx = row.dataset.idx;
            const detail = document.querySelector('tr.detail-row[data-idx="'+idx+'"]');
            if(detail){ detail.classList.toggle('hidden'); detail.classList.toggle('manual-hidden'); }
        });
    });

    // Data record expand/collapse
    document.body.addEventListener('click', (e)=>{
        const t = e.target;
        if(!(t instanceof HTMLElement)) return;
        if(t.classList.contains('data-summary')){
            const li = t.closest('.data-item');
            if(!li) return;
            const details = li.querySelector('.data-details');
            if(details){ details.classList.toggle('hidden'); li.classList.toggle('expanded'); }
        }
        // Check details expand/collapse
        if(t.classList.contains('check-summary') && t.dataset.hasDetails === 'true'){
            const li = t.closest('li');
            if(!li) return;
            const details = li.querySelector('.check-details');
            if(details){ details.classList.toggle('hidden'); }
        }
    });

    // Collapsible epics & stories
    document.querySelectorAll('.collapsible > .toggle').forEach(tg=>{
        tg.addEventListener('click', (e)=>{
            e.stopPropagation();
            const parent = tg.parentElement;
            if(!parent) return;
            parent.classList.toggle('expanded');
            const body = parent.querySelector('.group-body, .story-body');
            if(body) body.classList.toggle('hidden');
        });
    });
});
"""


def save_json_report(results: list[dict[str, Any]], json_path: str) -> bool:
    """Save test results to a JSON file.

    Args:
        results: List of test result dictionaries to save.
        json_path: Path where to save the JSON file.

    Returns:
        True if successfully saved, False if an error occurred.

    Note:
        Creates parent directories if they don't exist. Errors are silently ignored.
    """
    try:
        p = _pl.Path(json_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(_json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    except Exception:
        return False


def generate_html_report(
    results: list[dict[str, Any]],
    title: str,
    start_time: float,
    end_time: float,
    report_path: _pl.Path,
) -> bool:
    """Generate a complete HTML test report with interactive features.

    Args:
        results: List of test result dictionaries.
        title: Title for the HTML report.
        start_time: Test execution start timestamp.
        end_time: Test execution end timestamp.
        report_path: Path where to save the HTML file.

    Returns:
        True if successfully generated, False if an error occurred.

    Note:
        Creates a full-featured HTML report with theme switching, filtering,
        and timeline visualization. Groups tests by epic and story markers.
    """
    try:
        if start_time is not None:
            duration_total = end_time - float(start_time)
            start_str = _dt.datetime.fromtimestamp(float(start_time)).strftime("%Y-%m-%d %H:%M:%S")
            end_str = _dt.datetime.fromtimestamp(end_time).strftime("%Y-%m-%d %H:%M:%S")
            duration_str = f"{duration_total:.3f}s"
        else:
            start_str = end_str = duration_str = "—"

        counts = compute_counts(results)
        passed = counts.get("PASSED", 0)
        failed = counts.get("FAILED", 0)
        errors = counts.get("ERROR", 0)
        skipped = counts.get("SKIPPED", 0)
        xfail = counts.get("XFAIL", 0)
        xpass = counts.get("XPASS", 0)

        esc_title = escape_html(title)
        css = get_html_css()
        js = get_html_javascript()

        grouped: dict[str, dict[Any, list[dict[str, Any]]]] = {}
        ungrouped: list[dict[str, Any]] = []

        for r in results:
            epic = r.get("epic")
            story = r.get("story")
            if epic is None and story is None:
                ungrouped.append(r)
                continue
            epic_key = epic or "<no-epic>"
            grouped.setdefault(epic_key, {})
            story_key = story
            grouped[epic_key].setdefault(story_key, []).append(r)

        sections = _generate_html_sections(ungrouped, grouped)

        stats_parts = []
        if len(results) > 0:
            stats_parts.append(f"Total tests: {len(results)}")
            if passed > 0:
                stats_parts.append(f"Passed: {passed}")
            if failed > 0:
                stats_parts.append(f"Failed: {failed}")
            if errors > 0:
                stats_parts.append(f"Errors: {errors}")
            if skipped > 0:
                stats_parts.append(f"Skipped: {skipped}")
            if xfail > 0:
                stats_parts.append(f"Expected failures: {xfail}")
            if xpass > 0:
                stats_parts.append(f"Unexpected passes: {xpass}")

        stats_html = "".join(f"<div>{escape_html(stat)}</div>" for stat in stats_parts)

        html_doc = f"""<!DOCTYPE html>
<html lang='en'>
<head>
<meta charset='utf-8'/>
<title>{esc_title}</title>
<style>{css}</style>
</head>
<body class='theme-dark'>
<header><span class='title'>{esc_title}</span></header>
<button id='themeToggle' class='theme-toggle theme-toggle-floating' type='button' aria-label='Toggle theme'>Dark theme</button>
<div class='run-info'>
    <div>Start time: {escape_html(start_str)}</div>
    <div>End time: {escape_html(end_str)}</div>
    <div>Total duration: {escape_html(duration_str)}</div>
</div>
<div class='test-stats'>
    {stats_html}
</div>
{sections}
<footer>Generated by pytest-checkmate</footer>
<script>{js}</script>
</body>
</html>"""

        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(html_doc, encoding="utf-8")
        return True
    except Exception:
        return False


def _generate_html_sections(
    ungrouped: list[dict[str, Any]],
    grouped: dict[str, dict[Any, list[dict[str, Any]]]],
) -> str:
    """Generate HTML sections for test results organized by epic and story.

    Args:
        ungrouped: Tests without epic/story markers.
        grouped: Tests organized by epic and story structure.

    Returns:
        HTML string containing all test result sections.

    Note:
        Creates collapsible sections for epics and stories with
        interactive filtering and expandable test details.
    """
    sections: list[str] = []
    row_index = 0

    def build_rows(sub_results: list[dict[str, Any]], group_id: str) -> str:
        nonlocal row_index
        rows: list[str] = []
        for r in sub_results:
            idx = row_index
            row_index += 1
            short = escape_html(r.get("short", ""))

            has_custom_title = r.get("has_custom_title", False)
            params = r.get("params") or {}
            param_id = r.get("param_id")

            if has_custom_title and param_id:
                title_cell = f"{escape_html(r['title'])} [{escape_html(param_id)}]"
            elif has_custom_title and params:
                inline_params = ", ".join(f"{escape_html(str(k))}={escape_html(str(v))}" for k, v in params.items())
                title_cell = f"{escape_html(r['title'])} [{inline_params}]"
            elif not has_custom_title:
                title_cell = escape_html(r["title"])
            else:
                title_cell = escape_html(r["title"])
            timeline_html = format_timeline(r.get("steps", []), r.get("soft_checks", []), r.get("data_reports", []))
            errors_html = format_errors(r)
            function_name_header = f"<h4>Test function: {escape_html(r.get('name', ''))}</h4>" if r.get("name") else ""
            expanded = (
                f"<div class='detail-card status-{r['status']}'>"
                f"{function_name_header}{timeline_html}{errors_html}</div>"
            )
            rows.append(
                f"<tr class='status-{r['status']} main-row' data-group='{group_id}' data-status='{r['status']}' data-idx='{idx}'><td>{title_cell}</td>"
                f"<td class='status-cell'><span class='st-{r['status']}'>{r['status']}</span></td><td>{r['duration']:.3f}</td><td class='details'>{short}</td></tr>"
                f"<tr class='status-{r['status']} detail-row hidden manual-hidden' data-group='{group_id}' data-status='{r['status']}' data-idx='{idx}'><td colspan='4'>{expanded}</td></tr>",
            )
        return "".join(rows)

    def build_badges(sub_results: list[dict[str, Any]], group_id: str) -> str:
        counts = compute_counts(sub_results)
        total_local = sum(counts.values())
        desired = ["PASSED", "FAILED", "SKIPPED", "XFAIL"]
        ordered = [k for k in desired if k in counts] + [k for k in counts if k not in desired]
        parts = [
            f"<div class='badge' data-group='{group_id}' data-status='ALL'>ALL {total_local}</div>",
        ]
        parts += [
            f"<div class='badge' data-group='{group_id}' data-status='{escape_html(k)}'>{k} {counts[k]}</div>"
            for k in ordered
        ]
        return "".join(parts)

    if ungrouped:
        gid = "ungrouped"
        sections.append(
            f"<section class='group-section'>"
            f"<div class='summary' data-group='{gid}'>{build_badges(ungrouped, gid)}</div>"
            f"<table><thead><tr><th>Test</th><th>Status</th><th>Duration (s)</th><th>Details</th></tr></thead><tbody>{build_rows(ungrouped, gid)}</tbody></table></section>",
        )

    for epic_key in sorted(grouped.keys()):
        stories = grouped[epic_key]
        epic_display = escape_html(epic_key if epic_key != "<no-epic>" else "(No epic)")
        epic_all: list[dict[str, Any]] = []
        for lst in stories.values():
            epic_all.extend(lst)
        has_story = any(k is not None for k in stories)
        if has_story:
            story_blocks: list[str] = []
            for story_key in sorted(
                stories.keys(),
                key=lambda x: ("" if x is None else str(x).lower()),
            ):
                story_list = stories[story_key]
                story_display = escape_html(story_key) if story_key is not None else "(No story)"
                gid = f"epic-{slugify(epic_key)}-story-{slugify(str(story_key))}"
                story_blocks.append(
                    f"<div class='story-block collapsible' data-kind='story'>"
                    f"<h3 class='toggle' style='margin:14px 0 4px;'>Story: {story_display}</h3>"
                    f"<div class='story-body hidden'><div class='summary' data-group='{gid}'>{build_badges(story_list, gid)}</div>"
                    f"<table><thead><tr><th>Test</th><th>Status</th><th>Duration (s)</th><th>Details</th></tr></thead><tbody>{build_rows(story_list, gid)}</tbody></table></div>"
                    f"</div>",
                )
            sections.append(
                f"<section class='group-section collapsible' data-kind='epic'>"
                f"<h2 class='toggle' style='margin:36px 0 4px;'>Epic: {epic_display}</h2>"
                f"<div class='group-body hidden'>{''.join(story_blocks)}</div>"
                f"</section>",
            )
        else:
            gid = f"epic-{slugify(epic_key)}"
            sections.append(
                f"<section class='group-section collapsible' data-kind='epic'>"
                f"<h2 class='toggle' style='margin:36px 0 4px;'>Epic: {epic_display}</h2>"
                f"<div class='group-body hidden'><div class='summary' data-group='{gid}'>{build_badges(epic_all, gid)}</div>"
                f"<table><thead><tr><th>Test</th><th>Status</th><th>Duration (s)</th><th>Details</th></tr></thead><tbody>{build_rows(epic_all, gid)}</tbody></table></div>"
                f"</section>",
            )

    return "".join(sections) or "<p style='padding:12px 24px;'>No tests collected.</p>"
