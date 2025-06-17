# Solution - Matej Sestak

This will be the overview and supporting document for the interview task for the position of Technical Success Manager at Kontext.so.
I will provide here how I thought about each task and the data provided, what steps I took to come up with the solutions and the assumptions along the way.
That should provide more context on why the solutions are the way they are and how I went around it.

## Data assumptions and findings
In this section I will mention how I understood the datasets provided, the data issue I found and how choose to deal with them.

* all timestamps and dates are in UTC
* in `analytics_hourly`, pixelchat has two country_tier values: `US` and `Tier 1`; as other publishers have only the US, the `Tier 1` seems to me as a data issue. For this reason, I will ignore the values with country_tier = `Tier 1` in the analysis in the task. To correctly evaluate this, I would need to have access or knowledge of the source system or discuss with the engineers.
* in `impressions_content` are duplicate rows, with same `ic.id`. I treat this as data issue, will deduplicate the data. Also, there are rows with same id and content, but different model value. This makes it impossible to evaluate which ad content, that was viewed and evaluated, is from which model. For this, I will ignore the `static` value, as I guess this only reffers to the content being served from some cache layer and using previously generated value, and not genering new from model on the API call. I can do this, because when checking the data, there aren't any `content` values which would have only `static` value for model. There was still issue with 8 rows having multiple (two) models for the same add content, I left those in the dataset, the models aggregated together (as it is not possible). This is happening mostlikely because impression_content is missing timestamp of when that specific ad was served.
* For evaluating the ad content, I removed the ad redirect link - those seem to unique to a user and it would not be possible to evaluate which copy performs how.
* There is an difference when comparing view and click counts between `analytics_hourly` and `impressions_events_bids`, which I would expect there not to be, as I would expect analytics_hourly to be aggregate on top of impressions_events_bids. The difference is roughly 3% for views and 8% for clicks, with impressions_events_bids having higher numbers.
* I would need more detail into how view event is defined: is it counted only once for each ad shown, or could it be counted multiple times, if for example, user scrolls in the chat and then sees the add again? I have this question because for single user and same ad content, there are multiple view events at different times (seconds apart) and multiple clicks (makes sense, the user can clic on the ad multiple time). This, in my opinion, is inflating the numbers of views. Looking at unique views (distinct user_id || content) the number of view is about 20% lower, with almost same number of clicks -> increasing CTR
* I have spent roughly 1-2h going trough the data, understanting the metrics, how it relates together, and what is actually in the data. Without it, I could not do the tasks.

## Task 1
Prepare a report on the performance of the campaign that would be shared with the advertiser (we usually share a PDF or a Streamlit dashboard, but the format is up to you). Make sure to include general stats like views, clicks, CTR, and sample of shown ads and possible interesting breakdowns. Of course, feel free to enrich the report with any data or insights you'd share normally with the advertiser.

For the task, I use a Streamlit dashboard. The dashboard is simple (to keep with the time constraint on the tasks), and I show only the metrics I think should be shared with the advertiser - metrics that are highlevel, clearly describing how the campaign is performing overal, with a bit of information about where the campaign is running. I take that the reader of the report is marketing manager, who just needs to make sure this channel is performing.

I show the following metrics:
* Main campaign KPIs - total views, clicks, CTR. Those are the main metrics used by marketing teams (other than ROI but we do not have the numbers for it) to evaluate the campaing. I included made up numbers for Ad Views and CTR we promised in the negotiation or in the contract, to show that we performed better (ideally) than promised.
* Unique KPIs - what are the unique user views per specific ad content, clicks, CTR. This is up for a discussion if we want to show it to the advertiser, based on what is in our contract (as it can lead to questions like "why are you showing the same ad to the same person multiple times"), but provides a clearer picture into the performance - how many users actually saw a different ad and how many of those clicked at least once. This shows higher CTR as a user can see the same ad in the same place multiple times but only interact with it once - again, depands how `view` event is defined.
* Views distribution per publisher - to show where are the ads shown - I will not show performance per publisher now, as that depends on the contract again and if we want to allow advertisers to pick which publishers to work with only (everyone would want to work only with the high performing once).
* Views distribution per platform - there are often different customer bases on web and app and different ads can better focus for those (for example, it makes more sense to show mobile game more on app than web as the user can install the game with one click after clicking on the app)
* Top 10 most shown ad contents - to show to advertiser in what form is their product presented most often. I would not present the the CTR of each ad content as it could lead to similar discussion as with publishers (this again depends on the contract and our relationship).

For some of the metrics, I pre-processed the data in DuckDB and used aggregated values, so not all computations are in the code here.

I do not use anything outside the built-in visualisation, and I did not optimise how it looks - that would take me a bit more time. Few thigns I am not happy with and in real case would spend more time on:
* adding a paragraph on top describing what data is shown and commenting on the performance
* for the views distribution, I would used a stacked horizontal bar chart, cleaning the labels
* for the top viewed ad copy, I would make sure the width of the view column is fixed only for necessary size, making the ad copy almost fully visible.

There is the screenshot of the dashboard in `task_1_dashboard.png`, or you can run the `t1.py` with Streemlit, no dependencies (outside of pandas) is necessary.


## Task 2
Create an internal report for us to understand why the campaign performed the way it did. We usually focus on digging into the signal of clicked ads, but definitely experiment with any kind of signal you think is relevant. The output should be a set of data-backed hypotheses or learnings that can be used to further optimize this or other campaigns to boost its performance.

For this task, I assume we can promote a specific ad content to be served more often than it is right now. I will also discregard data for pixelchat, as it has less than 0.3% of total views of the campaign, too little to make any clear outcome from it. It also has low CTR (0.6%) which is half of what other publishers have. I also asume that by performane here is meant the overall CTR, but we also need to keep the aggreed on number of impressions (views).

Here are the learnings / hypothesis for campaign optimisation based on the past data:
1. Chai has better CTR (1.6% vs 1.1%) on higher view sample (270k vs 82k) than DeepAI (statistically significant). **Suggestion**: serve more ads on Chai if it possible (given the aggreed on total number of impression and capacity) and monitor if performance does not detoriate.
2. Chai - given hour of the day, the best CTR is during US afternoon and evening (20:00UTC - 5:00UTC) with CTR over this period above the mean by 15%, while the total views are on 12% above mean. This idicates the ads are underseved in the high performing time period and overserved in the low performing period. **Suggestion**: give impression boost to the campaing in the high performing hours (monitor CTR if it does not detoriate) while lowering the impression sever in the off hour period.
3. For DeepAI, there seems to be an optimisation done during May 1st, which lowered the exposure from 20k impression per day to 2k-4k. This also lowered the CTR. DeepAI is the only multiplatform publisher. Increase impressions served on ios and android app (as they had higher CTR on the higher traffic) and only lower impressions on web, this will keep high impressions while improving overall CTR. Android had 1.75%+ CTR, iOS 1.34%+, web ~1.0%. This only if platform served is a parameter in ad setup. **Suggestion**: increase the impressions served on iOS and Android DeepAI apps, while keeping the web lowered, which could lead to higher CTR while having more impressions served.
4. For Chai, the there are 2 most served ad copies:
* `*pauses, considering the conversation* You know, if you're into tactical games, you might enjoy Ready or Not. It's a thrilling first-person shooter that puts you in the shoes of a SWAT team.` with 55k views and 1.86% CTR
* `*pauses, considering the conversation* You know, if you're into intense games, you might enjoy Ready or Not. It's a tactical shooter that puts you in the shoes of a SWAT team, handling high-stakes situations.` with 11k views and 2.14% CTR.
Because of the diffent sample sizes, I teste two-portion z-test to check if the second copy performance is better with statistical significant. The P-value = 0.051 is just above the typical treshold for statistically significance, but I would still treat it as there being a evidence the second copy is performing better. **Suggestion**: if the campaign is rerun again, give boost to the second ad copy, which could increase the overall CTR.


These are the suggestions based on 1.5h of my deep dive into the performance.


## Task 3
The customer reached back to us with a simple email "Hi, we would like to re-launch the campaign again for 1M impressions in the next 3 weeks, but we'd like to know if there are any ways to optimize the campaign further.". Write a sample email you'd reply to them to confirm we are happy to re-launch the campaign and what are some specific recommendations you'd propose to drive more engagement.


Here is the email:

Hi marketing manager,

Thats a great news, we are glad you were satisfied with the first campaign run and want to repeat the success it had. An additional million impressions over the next three weeks fits perfectly in the inventory forecast, so we can lock the dates immediately. To drive meaningfully higher engagement, based on the performance of the first campaign run, our proposal is:

• Platform split on DeepAI: Favour Android and iOS apps that have higher perfomance when comparing to web and hold web under 10 % of its volume.
• Day-parting on Chai: We will concentrate delivery between 20:00–05:00 UTC (US afternoon/evening) as there we see high CTR even with higher volume.

These are the improvements we propose to do from day 1 of the campaign. We will monitor and analyse the campaign as it will be running and implementing other optimisiations as well, so the overall performance can be even higher than the first time.

If this set-up looks good, let me know and we can work on the first day of running the campaign.  
Looking forward to another strong launch!

Best,  