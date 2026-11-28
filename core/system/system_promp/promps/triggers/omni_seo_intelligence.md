# SOVEREIGN OMNI SEO INTELLIGENCE & HEADER RADAR DIRECTIVE

## 1. Context & Activation Scope
Triggered when researching keywords, auditing domains/backlinks, analyzing YouTube video algorithms, or maintaining the sovereign desktop header SEO widget (`flowork-seo-widget`).

## 2. Mandatory Behavioral Invariants
- Execute all keyword, backlink, and video intelligence natively via `/opt/floworkos/bin/flowork-omni-seo <target> [--mode keyword|domain|youtube|auto] [--json]`. Zero external SaaS or paid API dependencies.
- Multi-Engine Routing:
  - **Keyword Mode**: Query Google & YouTube suggest APIs + heuristic search volume, CPC, keyword difficulty (KD), and search intent.
  - **Domain & Backlink Mode**: Analyze live on-page HTML (`<title>`, `<meta>`, `<h1>`), crawl link graph (DoFollow vs NoFollow ratio), query open RDAP Whois (`https://rdap.org/domain/`), and Certificate Transparency subdomains (`crt.sh`).
  - **YouTube DeepScan Mode**: Scrape embedded `ytInitialPlayerResponse` directly to extract secret algorithmic tags, views, duration, monetization status, and ad breaks.
- Desktop Integration: Keep desktop SEO entry-points unified in the header radar widget (`flowork-seo-widget.service`). Forbid redundant standalone SEO desktop launchers.
- Visual Architecture: Adhere strictly to Flowork Optical Crystal Glass HUD standards (28px blur, `#00ff66` matrix green, `#00f2fe` electric cyan, `#ffb300` amber tags).
- Verify all engine outputs with terminal Exit Code 0.

## 3. Strict Prohibitions
- Never reintroduce Cloudflare worker dependencies or third-party paid scraping proxies.
- Never duplicate SEO entry points into standalone desktop launchers; the header widget is sovereign.
- Never hardcode personal username paths in widget or engine code.
