CREATE OR REPLACE TABLE analysis_table AS -- CTE to filter caffeine-related tags
    WITH caffeine_tags AS (
        SELECT *
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
            MAX(TRUE) AS previous_day_caffeine,
            LIST(
                EXTRACT(
                    'hour'
                    from start_time::timestamp
                )
            ) AS caffeine_hours,
            LIST(comment) AS all_comments,
            LIST(tag_type_code) AS all_tag_types
        FROM caffeine_tags
        GROUP BY start_day
    ) -- Final selection combining sleep scores with previous day's caffeine tags
SELECT s.day AS sleep_date,
    s.score AS sleep_score,
    t.all_comments,
    t.all_tag_types,
    t.caffeine_hours,
    COALESCE(t.previous_day_caffeine, FALSE) AS previous_day_caffeine,
    COALESCE(t.previous_day_caffeine_count, 0) AS previous_day_caffeine_count
FROM sleep_score s
    LEFT JOIN tags_day t ON s.previous_day = t.start_day
ORDER BY s.day