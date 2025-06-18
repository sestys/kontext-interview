## Solution - Matej Sestak

This is the overview and supporting document for the interview task for the position of Technical Success Manager at Kontext.so.
I will explain how I approached each task and the data provided, what steps I took to come up with the solutions, and the assumptions I made along the way.
This should provide context on why the solutions are the way they are and how I arrived at them.

## Data Assumptions and Findings

In this section, I explain how I understood the datasets provided, the data issues I found, and how I chose to deal with them.

* All timestamps and dates are in UTC.
* In `analytics_hourly`, Pixelchat has two `country_tier` values: `US` and `Tier 1`. Since other publishers have only `US`, the `Tier 1` label seems to be a data issue. Therefore, I ignore rows where `country_tier = 'Tier 1'`. To evaluate this correctly, I would need access to the source system or confirmation from the engineers.
* In `impressions_content`, there are duplicate rows with the same `ic.id`. I treat this as a data issue and deduplicate the data. There are also rows with the same ID and content but different model values, making it impossible to evaluate which model generated the ad content. I chose to ignore the `static` value, assuming it refers to cached content rather than newly generated content. This is valid because no content appears with only the `static` model. For the 8 rows with two different model values per ad, I kept them in the dataset but aggregated their performance.
* I removed ad redirect links from the content since they appear unique per user, making it impossible to evaluate ad copy performance.
* There's a discrepancy between view and click counts in `analytics_hourly` and `impressions_events_bids`. The latter reports \~3% more views and \~8% more clicks. I expected `analytics_hourly` to be an aggregate of the events file.
* I need more clarity on how `view` events are defined. Are they counted once per impression, or multiple times (e.g., if a user scrolls back to the ad)? There are cases of multiple view events (seconds apart) for the same user and ad content. This inflates view counts. Using unique views (distinct `user_id` + `content`) results in \~20% fewer views with similar click counts, thus increasing CTR.
* I spent around 1-2 hours reviewing the data, understanding the metrics and their relationships. This was essential before working on the tasks.

## Task 1

**Prepare a performance report of the campaign for the advertiser.**

For this, I used a Streamlit dashboard. The dashboard is simple due to time constraints and focuses only on metrics that should be shared with the advertiser—metrics that are high-level and clearly describe how the campaign performed overall, with some context about where the campaign ran. I assume the report reader is a marketing manager who primarily wants to verify channel performance.

Metrics shown:

* **Main campaign KPIs** – Total views, clicks, CTR. These are the primary metrics marketing teams use (aside from ROI, which we don’t have). I included placeholder targets for views and CTR to show we ideally outperformed what was promised.
* **Unique KPIs** – Unique user views per ad content, clicks, and CTR. This is up for discussion on whether to show to the advertiser (as it might raise questions like "why are you showing the same ad multiple times?"). But it gives a more accurate picture of performance.
* **Views distribution per publisher** – Shows where the ads were shown. I avoided showing performance per publisher to prevent advertisers from picking favorites (unless contractually allowed).
* **Views distribution per platform** – Highlights different audience segments (e.g., mobile app vs web). Helps tailor ad strategy.
* **Top 10 most-shown ad contents** – Shows how the advertiser’s product was most often presented. I didn't include CTRs here to avoid similar issues as with publishers.

Some metrics were preprocessed using DuckDB and used as aggregates in the dashboard.

The dashboard uses only built-in visualizations. I didn’t spend time on styling. Some parts I would improve in a real project:

* Add a paragraph explaining the data and summarizing performance
* Use a stacked horizontal bar chart with cleaned labels for view distributions
* Resize the ad copy column so the content is fully visible

A screenshot is saved in `task_1_dashboard.png`, or run `t1.py` in Streamlit. No dependencies beyond pandas.

## Task 2

**Internal report to understand why the campaign performed the way it did.**

I assume:

* We can boost the frequency of serving specific ad content.
* Pixelchat is excluded due to its low share (< 0.3%) and low CTR (0.6%).
* By "performance," CTR is the main success metric.
* We must still deliver the agreed number of impressions.

Learnings and hypotheses:

1. **Chai outperforms DeepAI** – 1.6% vs 1.1% CTR on a larger view base (270k vs 82k). Statistically significant.
   *Suggestion:* Prioritize Chai if impression cap allows and monitor CTR stability.
2. **Time-based performance on Chai** – Highest CTR during 20:00–05:00 UTC, which is 15% above average CTR and 12% above average volume. This idicates the ads are underseved in the high performing time period and overserved in the low performing period.
   *Suggestion:* Boost impressions during this window, reduce them during lower-performing hours.
3. **DeepAI platform split** – Post-May 1 changes dropped impressions (20k → 2-4k daily) and lowered CTR. DeepAI spans all platforms. Web underperforms (\~1.0% CTR) vs Android (1.75%) and iOS (1.34%).
   *Suggestion:* Increase app impressions, reduce web exposure if platform targeting is possible.
4. **Ad copy performance** – Two top Chai ad copies:

   * `*pauses, considering the conversation* You know, if you're into tactical games, you might enjoy Ready or Not. It's a thrilling first-person shooter that puts you in the shoes of a SWAT team.`: 55k views, 1.86% CTR
   * `*pauses, considering the conversation* You know, if you're into intense games, you might enjoy Ready or Not. It's a tactical shooter that puts you in the shoes of a SWAT team, handling high-stakes situations.`: 11k views, 2.14% CTR
     A two-proportion z-test yields p = 0.051, which is borderline for statistically significance, but I would still treat it as there being a evidence the second copy is performing better..
     *Suggestion:* Give more weight to the second copy if rerunning the campaign.

These findings are based on \~1.5 hours of performance deep-dive.

## Task 3

**Email reply to client asking about relaunch and optimisation.**

---

Hi Marketing Manager,

That's great news! We're glad you were happy with the first run and excited to repeat the success. The additional 1M impressions fit well into the forecast, and we can lock in the dates immediately.

To drive even stronger engagement this time, based on past performance, we recommend:

• **Platform split on DeepAI** – Prioritize Android and iOS (higher CTRs) and limit web to under 10%.
• **Day-parting on Chai** – Concentrate impressions between 20:00–05:00 UTC (US afternoon/evening), which saw strong CTRs even at high volume.

These improvements will be active from day one. We'll monitor the campaign continuously and implement further optimizations as needed to exceed the first campaign’s performance.

Let me know if this setup works, and we’ll schedule the launch!

Looking forward to another strong run.

Best,

Matej from Kontext
