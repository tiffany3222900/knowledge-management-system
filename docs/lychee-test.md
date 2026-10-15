# Lychee Link Checker Test

> **TEMPORARY TEST FIXTURE** — this file is intentionally created with broken
> links to verify the Lychee gate. It will be deleted after the test.

## Test cases

- [Missing internal file](does-not-exist.md) — should be reported: file not found
- [Invalid domain](https://example.invalid/toner-guide) — should be reported: unresolvable domain
- [404 external page](https://www.example.com/no-such-page) — should be reported: HTTP 404
- [Ignored GitHub edit link](https://github.com/tiffany3222900/knowledge-management-system/edit/main/docs/faq.md) — should be EXCLUDED by .lycheeignore
- [Existing internal file](faq.md) — should pass
- [Valid external site](https://www.example.com) — should pass
