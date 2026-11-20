# Asset licensing and public distribution

## Institutional logo

The local `web/assets/kle-logo.jpg` is an institutional logo. No license or redistribution permission for the logo was found in the repository. It is excluded from Git by `.gitignore`; the original local file is left untouched. The copy under `data/source/` is part of the private, ignored input bundle.

The public checkout uses a text wordmark instead. PDF report generation includes the logo only when the local asset exists, so a clean clone can generate reports without it. Obtain written permission or provide an approved replacement asset before adding a logo to a public distribution.

## Web fonts

The original `web/assets/NimbusSans-Regular.otf` and `web/assets/P052-Roman.otf` are local-only and excluded from Git. The repository's `docs/PDF_FONT_LICENSE.txt` identifies the URW Base 35 family as AGPL-3 with a font exception, but it does not include the full upstream `COPYING` text or establish file-level provenance for these exact binaries. Until that is confirmed and the required complete notices are supplied, these binaries are not included in public distribution. The frontend uses system font fallbacks when they are absent.

## PDF fonts

`data/fonts/DejaVuSans.ttf`, `DejaVuSans-Bold.ttf`, and `DejaVuSerif.ttf` remain in the repository with the Bitstream Vera/DejaVu redistribution notice in `docs/FONT_LICENSE.txt`. Preserve that notice when redistributing the font files.

## Project license

The root `LICENSE` explicitly states that no project license has been selected. Third-party font terms do not grant a license to the application source. Do not add an open-source project license without the owner's approval.
