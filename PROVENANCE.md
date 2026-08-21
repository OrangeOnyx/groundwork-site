# Asset Provenance

The August 21 handover export (ASSETS.md) noted that the hero footage's generation records were not in the project archive. They exist, and this file is that record.

## Hero footage and stills

All six visual assets were generated on August 14, 2026 in Adam Abdalla's own Higgsfield account, for this project, in a Claude Code build session:

| File | How it was made |
|---|---|
| `assets/hero-scrub.mp4` | Three 6-second segments generated with **Seedance 2.0** (image-to-video, 1080p, 16:9, std mode, no audio), chained by feeding each segment's final frame in as the next segment's start image, then joined and re-encoded with ffmpeg (single encode, `-g 8` keyframes) into one 18-second scrub file. The starting frame was generated with **Nano Banana Pro** (16:9, 2k). |
| `assets/hero-poster.jpg` | First frame of the joined video, extracted with ffmpeg. |
| `assets/hero-ending.jpg` | Final frame of the joined video, extracted with ffmpeg. |
| `assets/still-scatter.jpg` | Generated with Nano Banana Pro, same world and grade as the film. |
| `assets/still-constellation.jpg` | Generated with Nano Banana Pro, same world and grade. |
| `assets/still-ground.jpg` | Generated with Nano Banana Pro, same world and grade. |

The full generation prompts, the storyboard, and the model settings are preserved in the project design package (`design-package.md` in the private build archive, `Projects/Ai Onboarding` on Adam's machine, also in the private repo OrangeOnyx/groundwork).

## Rights

The footage was generated under Adam Abdalla's paid Higgsfield subscription for this project. It is owner-produced work, not third-party stock. No third-party footage, stock photography, or licensed imagery appears anywhere on the site.

## Fonts

Libre Caslon Display, Public Sans, and IBM Plex Mono load from Google Fonts under the SIL Open Font License 1.1.
