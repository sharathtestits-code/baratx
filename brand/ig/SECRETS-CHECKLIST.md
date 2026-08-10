# Secrets needed for Drive → IG automation / cloud agents

**Do not commit secret values to git.** Store in Cursor environment secrets and/or `~/.config/baratx/`.

## Google Drive
| Name | Value |
| --- | --- |
| `GOOGLE_DRIVE_SERVICE_ACCOUNT_JSON` | Full JSON from `baratx-bb47bc5535a4.json` |
| File fallback | `~/.config/baratx/google-drive.json` |
| SA email (share folder Editor) | `barathx@baratx.iam.gserviceaccount.com` |
| Folder ID | `16q4vDZWnIn4wFr5IEAXlswVHUH2lw6aF` |

## Instagram (@getbarathx)
| Name | Value |
| --- | --- |
| `INSTAGRAM_ACCESS_TOKEN` | Page/user token (kept in `~/.config/baratx/instagram.env` + Railway prod) |
| `INSTAGRAM_BUSINESS_ACCOUNT_ID` | `17841441378296886` |
| `PAGE_ID` (optional) | `1140135129194509` |
| File fallback | `~/.config/baratx/instagram.env` |

## Railway (prod charming-sparkle / baratx)
Already set: `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `DISABLE_INSTAGRAM_SCHEDULE=0`, `INSTAGRAM_IMAGE_BASE` (grunge).

## Cursor Automations
When creating **BarathX Drive Social Draft → IG**, add the same Drive + IG env vars to the automation’s cloud environment so runs outside this VM still work.
