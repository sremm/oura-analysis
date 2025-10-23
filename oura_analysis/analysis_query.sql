CREATE OR REPLACE TABLE analysis_table AS -- CTE to filter caffeine-related tags
    WITH caffeine_tags AS (
        SELECT *,
            EXTRACT(
                'hour'
                from start_time::timestamp
            ) AS caffeine_hour,
            FROM tags
        WHERE comment = 'Coffee'
            OR tag_type_code IN ('tag_generic_coffee', 'tag_generic_caffeine')
            OR (
                tag_type_code = 'custom'
                AND custom_name = 'Mate'
            )
    ),
    tags_day AS (
        SELECT start_day,
            COUNT(*) AS previous_day_caffeine_count,
            COUNT(*) FILTER (
                WHERE caffeine_hour < 13
            ) as caffeine_count_before_1pm,
            COUNT(*) FILTER (
                WHERE caffeine_hour >= 13
            ) as caffeine_count_after_1pm,
            -- single readable timing column derived from the counts
            CASE
                WHEN COUNT(*) = 0 THEN 'None'
                WHEN COUNT(*) FILTER (
                    WHERE caffeine_hour < 13
                ) > 0
                AND COUNT(*) FILTER (
                    WHERE caffeine_hour >= 13
                ) > 0 THEN 'Before and After 1 PM'
                WHEN COUNT(*) FILTER (
                    WHERE caffeine_hour < 13
                ) > 0 THEN 'Before 1 PM'
                WHEN COUNT(*) FILTER (
                    WHERE caffeine_hour >= 13
                ) > 0 THEN 'After 1 PM'
                ELSE 'None'
            END AS caffeine_timing,
            LIST(caffeine_hour) AS caffeine_hours,
            LIST(comment) AS all_comments,
            LIST(tag_type_code) AS all_tag_types
        FROM caffeine_tags
        GROUP BY start_day
    ) -- Final selection combining sleep scores with previous day's caffeine tags
SELECT s.day AS sleep_date,
    s.day AS sleep_date,
    s.score AS sleep_score,
    t.all_comments,
    t.all_tag_types,
    t.caffeine_hours,
    COALESCE(t.caffeine_timing, 'None') AS caffeine_timing,
    COALESCE(t.previous_day_caffeine_count, 0) AS previous_day_caffeine_count,
    COALESCE(t.caffeine_count_before_1pm, 0) AS caffeine_count_before_1pm,
    COALESCE(t.caffeine_count_after_1pm, 0) AS caffeine_count_after_1pm
FROM sleep_score s
    LEFT JOIN tags_day t ON s.previous_day = t.start_day
ORDER BY s.day