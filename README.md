# suvastika.com - Supabase Backup

Full backup of the Supabase project (nlsmuvtvhnlczqdyfdyo) that previously powered suvastika.com.

Contents (populated automatically by GitHub Action on first push):

- storage/blog-images/ - 1,148 blog post images, organized by post slug (featured.jpg = cover, content-N.jpg = in-post images)
- storage/media/ - 56 product and about-page images
- storage/patents/ - 42 patent certificate PDFs and images
- database/ - full website content as JSON: posts (326), news (224), pages (63), products (39), patents (14), categories, tags, site_settings, speaking_events

How it works: list1.txt, list2.txt, list3.txt and list_media_patents.txt contain the full file inventory. The workflow .github/workflows/import-backup.yml runs import_backup.py, which downloads every file from Supabase public storage, exports the database tables, and commits the result to this repo.

Created 2026-06-12 with Claude.
