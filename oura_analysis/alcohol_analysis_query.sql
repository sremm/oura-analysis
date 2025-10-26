CREATE OR REPLACE TABLE analysis_table AS WITH -- CTE to get alcohol related tags with hour extracted
    sleep_with_previous_day_bedtime AS (
        SELECT *,
            LAG(bedtime_start) OVER (
                ORDER BY day
            ) AS previous_day_bedtime_start
        FROM sleep
    ),
    tags_with_previous_day_bedtime AS (
        SELECT t.*,
            s.previous_day_bedtime_start AS previous_day_bedtime_start
        FROM tags t
            JOIN sleep_with_previous_day_bedtime s ON t.start_day = s.day
    ),
    -- determine which tags belong to previous day based on bedtime
    start_day_adjusted_tags AS (
        SELECT *,
            CASE
                WHEN start_time::TIMESTAMPTZ < previous_day_bedtime_start::TIMESTAMPTZ THEN start_day - INTERVAL '1 day'
                ELSE start_day
            END AS adjusted_start_day
        FROM tags_with_previous_day_bedtime
    ),
    -- select only alcohol related tags from adjusted tags
    alcohol_tags AS (
        SELECT *,
            EXTRACT(
                'hour'
                from start_time::TIMESTAMPTZ
            ) AS alcohol_hour
        FROM start_day_adjusted_tags
        WHERE tag_type_code IN (
                'tag_sleep_alcohol',
                'tag_generic_wine',
                'tag_generic_beer'
            )
    ),
    tags_day AS (
        SELECT adjusted_start_day AS adjusted_start_day,
            COUNT(*) AS previous_day_alcohol_count,
            MAX(alcohol_hour) AS last_alcohol_hour,
            LIST(alcohol_hour) AS alcohol_hours,
            LIST(comment) AS all_comments,
            LIST(tag_type_code) AS all_tag_types
        FROM alcohol_tags
        GROUP BY adjusted_start_day
    ) -- Final selection combining sleep scores with previous day' s alcohol tags
SELECT s.day AS sleep_date,
    s.score AS sleep_score,
    t.all_comments,
    t.all_tag_types,
    t.alcohol_hours,
    COALESCE(t.last_alcohol_hour, -1) AS last_alcohol_hour,
    COALESCE(t.previous_day_alcohol_count, 0) AS previous_day_alcohol_count
FROM sleep_score s
    LEFT JOIN tags_day t ON s.previous_day = t.adjusted_start_day
ORDER BY s.day