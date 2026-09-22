select
    review_id,
    order_id,
    review_score,
    review_comment_title,
    review_comment_message,
    review_creation_date::timestamp as review_creation_at,
    review_answer_timestamp::timestamp as review_answered_at
from {{ source('raw', 'order_reviews') }}
