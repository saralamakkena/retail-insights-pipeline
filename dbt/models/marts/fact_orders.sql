with order_items as (

    select * from {{ ref('stg_order_items') }}

),

orders as (

    select * from {{ ref('stg_orders') }}

),

order_payments as (

    -- Payments are recorded per order (e.g. split across installments), not
    -- per item, so aggregate to one total per order before joining. This
    -- total repeats across every item row belonging to the same order,
    -- since this fact table's grain is one row per order item.
    select
        order_id,
        sum(payment_value) as total_payment_value

    from {{ ref('stg_order_payments') }}
    group by order_id

),

final as (

    select
        order_items.order_id,
        order_items.order_item_id,
        orders.customer_id,
        order_items.product_id,
        order_items.seller_id,
        orders.order_status,
        orders.order_purchase_at,
        orders.order_delivered_customer_at,
        order_items.price,
        order_items.freight_value,
        order_payments.total_payment_value

    from order_items
    inner join orders
        on order_items.order_id = orders.order_id
    left join order_payments
        on order_items.order_id = order_payments.order_id

)

select * from final