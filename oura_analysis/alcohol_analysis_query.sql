CREATE OR REPLACE TABLE analysis_table AS -- CTE to filter caffeine-related tags
    WITH alcohol_tags AS (
        SELECT *,
            EXTRACT(
                'hour'
                from start_time::timestamp
            ) AS alcohol_hour,
            FROM tags
        WHERE tag_type_code IN (
                'tag_sleep_alcohol',
                'tag_generic_wine',
                'tag_generic_beer'
            )
    ),
    tags_day AS (
        SELECT start_day,
            COUNT(*) AS previous_day_alcohol_count,
            MAX(alcohol_hour) AS last_alcohol_hour,
            LIST(alcohol_hour) AS alcohol_hours,
            LIST(comment) AS all_comments,
            LIST(tag_type_code) AS all_tag_types
        FROM alcohol_tags
        GROUP BY start_day
    ) -- Final selection combining sleep scores with previous day' s alcohol tags
SELECT s.day AS sleep_date,
    s.score AS sleep_score,
    t.all_comments,
    t.all_tag_types,
    t.alcohol_hours,
    COALESCE(t.last_alcohol_hour, -1) AS last_alcohol_hour,
    COALESCE(t.previous_day_alcohol_count, 0) AS previous_day_alcohol_count
FROM sleep_score s
    LEFT JOIN tags_day t ON s.previous_day = t.start_day
ORDER BY s.day