# Fieldnotes - product notes

Fieldnotes is our mobile app for site inspectors. Inspectors record findings on site, photos included, and the report is put together back at the office.

## How it works

An inspector opens a job, works through the checklist for that job type, and adds notes and photos as they go. Everything is saved on the device first. When there's a connection, the job syncs to the office account and the report can be generated as a PDF.

Sync is deliberately boring: last write wins for checklist answers, and photos are never overwritten, only added. Most sync arguments in testing turned out to be two people editing the same job, so since version 2.4 the app warns you if someone else has the job open.

## Offline mode

The app has to work in basements, plant rooms and rural sites with no signal, so offline mode is not a fallback, it's the normal case. The full checklist and the last 90 days of jobs are kept on the device. A job created offline gets a temporary reference starting with OFF- and is given a real reference when it syncs.

If sync fails three times the app stops retrying in the background and shows a banner. Retrying forever was draining batteries in the first version.

## Pricing

Fieldnotes is sold per inspector, not per report. The standard plan is 29 pounds per user per month and includes unlimited jobs and reports. The small team plan is 99 pounds a month for up to five inspectors.

There is no free plan. There is a 30 day trial, no card required, because our sales cycle is mostly word of mouth through trade associations.

## Known problems

PDF generation fails on reports with more than about 120 photos. The report service runs out of memory. It's on the list for this quarter - the fix is probably streaming the images rather than loading them all at once.

Android tablets older than Android 10 are not supported. The camera library we use needs the newer camera API and maintaining the old path was taking more time than the devices are worth.
