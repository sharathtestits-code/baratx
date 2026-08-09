# BarathX QA — Feature matrix (for automation agents)

Use this as the source of truth for login + end-to-end coverage. Base URL: `https://barathx.com` · API: `https://baratx-production.up.railway.app`.

## Test accounts (set locally — never commit passwords)

| Role | How to sign in | Notes |
|------|----------------|-------|
| Member A | Email/password or Google test user | Primary poster |
| Member B | Second email account | Follower / replier |
| Official | `sharath` or `baratx` + `OFFICIAL_ACCOUNT_PASSWORD` | Ops |
| Admin console | `/admin` + `ADMIN_SECRET` | No user JWT |

Env for agent (secrets manager / local `.env.qa`, gitignored):
```
QA_BASE_URL=https://barathx.com
QA_API_BASE=https://baratx-production.up.railway.app
QA_USER_A_EMAIL=
QA_USER_A_PASSWORD=
QA_USER_B_EMAIL=
QA_USER_B_PASSWORD=
QA_OFFICIAL_USER=sharath
QA_OFFICIAL_PASSWORD=
QA_ADMIN_SECRET=
```

## Auth

| ID | Feature | Steps | Expect |
|----|---------|-------|--------|
| A1 | Email signup | `/signup` → email/pass/username → submit | Lands Square / first-session; verify email banner if unverified |
| A2 | Email login | `/login` | Opens Square |
| A3 | Google login | `/login` Google button | Opens Square (needs `GOOGLE_CLIENT_ID`) |
| A4 | Logout | Settings / profile menu | Returns to landing or login |
| A5 | Forgot password | `/forgot-password` | Email sent when Resend configured |

## Square (Home)

| ID | Feature | Steps | Expect |
|----|---------|-------|--------|
| S1 | For you feed | `/feed` → For you | Community takes above official digest; not only people you follow |
| S2 | Following feed | Following tab | Only followed + self |
| S3 | Compose take | Write + Post | Post appears; Alerts for followers + @baratx/@sharath |
| S4 | Hot take starters | Open starters → pick | Fills compose (not LLM) |
| S5 | First session | New user | Arena + take + city; **Skip for now** works |
| S6 | Nav tour | After first session | 3 steps Square / Alerts / Arenas; **Skip tour** works |
| S7 | Like / reply / repost | On a post | Counts update; author gets Alert + email if configured |

## Alerts & email

| ID | Feature | Steps | Expect |
|----|---------|-------|--------|
| N1 | Bottom Alerts | Nav Alerts | Badge when unread; `/notifications` list |
| N2 | Menu Alerts | ☰ menu → Alerts | Unread chip; opens `/notifications` |
| N3 | Reply Alert | B replies to A | A sees “replied to your post” |
| N4 | Post Alert (follower) | A posts; B follows A | B sees “posted in the Square” |
| N5 | Activity email | Same as N3/N4 with Resend | Email CTA to post or login |

## Arenas / Live / Communities

| ID | Feature | Steps | Expect |
|----|---------|-------|--------|
| R1 | Arenas list | `/arenas` | Six arenas |
| R2 | Arena detail | Open Sports etc. | Topics / join |
| R3 | Pick a side | Debate space | For/Against posts |
| R4 | Live list | `/spaces` | Rooms; Start a live |
| R5 | Live room | Enter room | Chat / Live Talk if enabled |
| R6 | Communities | `/communities` | Not the same as Arenas |

## Profile / social

| ID | Feature | Steps | Expect |
|----|---------|-------|--------|
| P1 | Profile | `/u/{user}` | Posts, follow |
| P2 | Follow | Follow B from A | B gets follow Alert |
| P3 | Search | `/search` | Users + posts |
| P4 | Messages | `/messages` | Thread send/receive |
| P5 | Bookmarks | Bookmark post → `/bookmarks` | Listed |
| P6 | Settings | Theme / privacy | Persists |

## Rewards / admin

| ID | Feature | Steps | Expect |
|----|---------|-------|--------|
| W1 | Rewards | `/rewards` | Founding + Race copy |
| W2 | Admin unlock | `/admin` + secret | Overview tabs |
| W3 | Admin engage | Engage tab | List new posts; comment as official |
| W4 | Admin tools | Digest / prompts | Success or skip message |

## Legal / public

| ID | Feature | Path |
|----|---------|------|
| L1 | Landing | `/` |
| L2 | Terms | `/terms` |
| L3 | Privacy | `/privacy` |
| L4 | Guidelines | `/guidelines` |

## Smoke order for an automation agent

1. A2 login as Member A  
2. S1 feed loads community posts  
3. S3 post a unique string `qa-{timestamp}`  
4. Login Member B (following A) → N4 Alert contains that string  
5. B replies → A sees N3  
6. N2 menu Alerts badge  
7. R1 → R4 smoke  
8. W2 admin unlock  
9. A4 logout  

## Out of scope for v1 automation

- Real UPI payouts  
- Instagram publish  
- Phone OTP (MSG91) unless staging numbers exist  
- LLM features (not shipped yet — see `brand/product/ROADMAP_AI_LEGAL_CLOUD.md`)
