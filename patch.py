#!/usr/bin/env python3
"""
Apply status-site-specific additions to the raw ops_dashboard_index.html
fetched from the main repo. Run by sync.yml before committing.

Usage: python3 patch.py index_raw.html > index_new.html
"""
import re
import sys

FAVICON_SVG = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 30 30'%3E"
    "%3Crect width='30' height='30' rx='6.5' fill='%230d1f35' stroke='%2300d4aa' stroke-width='1.5'/%3E"
    "%3Crect x='5' y='18' width='4' height='7' rx='1' fill='%2300d4aa' opacity='.55'/%3E"
    "%3Crect x='12' y='13' width='4' height='12' rx='1' fill='%2300d4aa' opacity='.75'/%3E"
    "%3Crect x='19' y='8' width='4' height='17' rx='1' fill='%2300d4aa'/%3E"
    "%3Ccircle cx='21' cy='6' r='2.2' fill='%2300d4aa'/%3E%3C/svg%3E"
)

HEAD_INJECT = f"""\
  <link rel="icon" type="image/svg+xml" href="{FAVICON_SVG}" />
  <link rel="apple-touch-icon" href="/icon-192.png" />
  <link rel="manifest" href="/manifest.json" />
  <meta name="apple-mobile-web-app-capable" content="yes" />
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
  <meta name="apple-mobile-web-app-title" content="AT Ops" />
  <meta name="theme-color" content="#0d1424" />"""

LOGO_SVG = """\
      <svg width="30" height="30" viewBox="0 0 30 30" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="flex-shrink:0">
        <rect x="0.75" y="0.75" width="28.5" height="28.5" rx="6.5" fill="#0d1f35" stroke="#00d4aa" stroke-width="1.5"/>
        <rect x="6"  y="19" width="4" height="6"  rx="1" fill="#00d4aa" opacity="0.55"/>
        <rect x="13" y="14" width="4" height="11" rx="1" fill="#00d4aa" opacity="0.75"/>
        <rect x="20" y="9"  width="4" height="16" rx="1" fill="#00d4aa"/>
        <circle cx="22" cy="7" r="2.2" fill="#00d4aa"/>
      </svg>"""

LOGOUT_BTN = '      <a href="/cdn-cgi/access/logout" class="logout-btn">Sign out</a>'

LOGOUT_CSS = """\
    .logout-btn {
      font-size: 0.75rem;
      color: var(--text-muted);
      text-decoration: none;
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 0.25rem 0.625rem;
      transition: color 0.2s, border-color 0.2s;
      white-space: nowrap;
    }

    .logout-btn:hover {
      color: var(--text);
      border-color: var(--border-solid);
    }"""

MOBILE_CSS = """\
    @media (max-width: 600px) {
      .badge-internal { display: none; }
      .header-logo { font-size: 0.875rem; }
      .logout-btn { padding: 0.25rem 0.5rem; font-size: 0.6875rem; }
      .data-table th:nth-child(3),
      .data-table td:nth-child(3),
      .data-table th:nth-child(4),
      .data-table td:nth-child(4),
      .data-table th:nth-child(5),
      .data-table td:nth-child(5) { display: none; }
    }"""


def patch(html: str) -> str:
    # 1. Head tags after <meta charset>
    charset = '<meta charset="UTF-8" />'
    if 'rel="manifest"' not in html and charset in html:
        html = html.replace(charset, charset + '\n' + HEAD_INJECT, 1)

    # 2. Logout button CSS + mobile overrides before closing </style>
    if '.logout-btn' not in html:
        html = html.replace('  </style>', LOGOUT_CSS + '\n\n  </style>', 1)
    if 'badge-internal { display: none' not in html:
        html = html.replace('  </style>', MOBILE_CSS + '\n\n  </style>', 1)

    # 3. Logo SVG — strip any existing SVG in the header-left, then inject ours
    logo_marker = '      <span class="header-logo">'
    if logo_marker in html:
        # Remove any SVG element that immediately precedes the header-logo span
        html = re.sub(r'<svg[\s\S]*?</svg>\s*\n\s*(?=\s*<span class="header-logo">)', '', html)
        if 'circle cx="22"' not in html:
            html = html.replace(logo_marker, LOGO_SVG + '\n' + logo_marker, 1)

    # 4. Logout button before the closing </div></header>
    logout_marker = '\n    </div>\n  </header>'
    if '/cdn-cgi/access/logout' not in html and logout_marker in html:
        html = html.replace(
            logout_marker,
            '\n' + LOGOUT_BTN + logout_marker,
            1,
        )

    return html


if __name__ == '__main__':
    path = sys.argv[1] if len(sys.argv) > 1 else 'index_raw.html'
    with open(path) as f:
        html = f.read()
    sys.stdout.write(patch(html))
