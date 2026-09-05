# Asset Provenance

Every raster shipped on this site is recorded here, and each carries its origin embedded in the file itself (PNG tEXt / JPEG COM chunk).

## Current assets (the Annual Report world, August 2026)

| File | How it was made |
|---|---|
| `assets/og-card.png` | The social-share card (1200x630). Rendered August 26, 2026 from an HTML composition in the site's own design system (paper ground, Archivo 900 headline, Besley italic sub, the stacked-bars system mark) via headless Edge. Drawn, not AI-generated. |
| `assets/explainer/groundwork-hero-loop-15s.mp4` | Silent ~15s, 1920×1080, h264 cover loop. Mark-build language only (rule → scatter → stacked bars → Operator disc → Remember·Improve frame → leave-with). Approved cut, reconstructed from Shipper parts on `assets/hero-loop-explainer` (1,657,879 bytes; sha256 prefix `12db6920fb714a7c`). |
| `assets/explainer/hero-loop-poster.png` | Still frame for the cover loop (reduced-motion and preload poster). 1920×1080 PNG from the same Shipper parts (578,426 bytes; sha256 prefix `3f7812ad5e4c0f35`). |
| `apple-touch-icon.png` | The Groundwork mark (three terracotta layer bars, mustard Operator disc, ink ground line on paper) rendered from inline SVG via headless Edge at 512px, scaled to 180px with ffmpeg. Drawn, not AI-generated. |
| `favicon.ico` | Same mark, scaled to 48px with ffmpeg. The pages also carry the mark as an inline SVG favicon. |
| `assets/atlas/atlas-*.png` (six sheets: D-1 dashboard, A-1 site plan, A-2 spatial, R-1 rent roll with unit drawer, W-1 action board, AI-1 concierge) | Screenshots from the Atlas operator manual. The tool, the sheet system, and the property geometry are real; tenant names and figures are the manual's demonstration dataset, kept separate from the live records. Cleared for public use (August 2026). Not AI-generated. |

## Retired assets (the original film world, August 2026 and earlier)

The site's first visual world was built around an 18-second scroll-scrubbed hero film and three stills, generated on August 14, 2026 in Adam Abdalla's own Higgsfield account for this project (Seedance 2.0 segments chained from Nano Banana Pro start frames, joined with ffmpeg). Those six assets (`hero-scrub.mp4`, `hero-poster.jpg`, `hero-ending.jpg`, `still-scatter.jpg`, `still-constellation.jpg`, `still-ground.jpg`) were retired with the August 2026 redesign and removed from the deploy; they remain in this repository's git history, and the full generation prompts, storyboard, and model settings are preserved in the project design package (`design-package.md` in the private build archive, also in the private repo OrangeOnyx/groundwork). The original A-2 aerial screenshot (`assets/atlas-spatial.jpg`) was likewise retired in August 2026 when the manual sheet set above replaced it.

## Rights

All imagery is owner-produced work or the owner's own property records. The retired footage was generated under Adam Abdalla's paid Higgsfield subscription for this project. No third-party footage, stock photography, or licensed imagery appears anywhere on the site.

## Fonts

Archivo, Besley, and Courier Prime load from Google Fonts under the SIL Open Font License 1.1.
