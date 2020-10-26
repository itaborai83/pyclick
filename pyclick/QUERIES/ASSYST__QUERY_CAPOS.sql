select    a.message_id
,        a.message_sc
,        b.message_cat_id
,        b.message_cat_sc
,        b.message_cat_n
,        a.message_n
,        a.message_rmk
,        a.active_from
,        a.active_until
,        a.content
from    message as a
        --
        inner join message_cat as b
        on     a.message_cat_id = b.message_cat_id
        --
where    1=1
and        b.message_cat_sc = 'CAPO'
and        a.active_until >= CONVERT(DATETIME, '2020-10-01 00:00:00', 120)
and        a.active_from <= CONVERT(DATETIME, '2020-10-22 23:59:59', 120)