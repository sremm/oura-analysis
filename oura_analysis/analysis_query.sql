CREATE OR REPLACE TABLE analysis_table AS WITH tags_day AS (
        SELECT start_day,
            /* Count all caffeine-related tags */
            COUNT(*) FILTER (
                WHERE comment = 'Coffee'
                    OR tag_type_code IN ('tag_generic_coffee', 'tag_generic_caffeine')
                    OR (
                        tag_type_code = 'custom'
                        AND custom_name = 'Mate'
                    )
            ) AS previous_day_caffeine_count,
            MAX(
                CASE
                    WHEN comment = 'Coffee' THEN TRUE
                    WHEN tag_type_code IN ('tag_generic_coffee', 'tag_generic_caffeine') THEN TRUE
                    WHEN tag_type_code = 'custom'
                    AND custom_name = 'Mate' THEN TRUE
                    ELSE FALSE
                END
            ) AS previous_day_caffeine,
            LIST(comment) AS all_comments,
            LIST(tag_type_code) AS all_tag_types
        FROM tags
        GROUP BY start_day
    )
SELECT s.day AS sleep_date,
    s.score AS sleep_score,
    t.all_comments,
    t.all_tag_types,
    COALESCE(t.previous_day_caffeine, FALSE) AS previous_day_caffeine,
    COALESCE(t.previous_day_caffeine_count, 0) AS previous_day_caffeine_count
FROM sleep_score s
    LEFT JOIN tags_day t ON s.previous_day = t.start_day
ORDER BY s.day