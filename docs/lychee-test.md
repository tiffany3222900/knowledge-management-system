# Lychee Link Checker Test

> **TEMPORARY TEST FIXTURE** — this file is intentionally created with broken
> links to verify the Lychee gate. It will be deleted after the test.

## Test cases

- [Missing internal file](does-not-exist.md) — should be reported: file not found
- [Nonexistent domain](https://definitely-not-a-real-domain-xyz123.com/toner-guide) — should be reported: DNS failure
- [404 external page](https://httpstat.us/404) — should be reported: HTTP 404
- [Ignored GitHub edit link](https://github.com/tiffany3222900/knowledge-management-system/edit/main/docs/faq.md) — should be EXCLUDED by .lycheeignore
- [Existing internal file](faq.md) — should pass
- [Valid external site](https://www.wikipedia.org) — should pass
