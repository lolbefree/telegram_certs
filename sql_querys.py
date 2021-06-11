def get_certificate(x):
    return f"""select id from bigcert_header
where tel={x}"""


def history(tel):
    return f"""
      if not exists(
    select b.wrkordno, convert(varchar(20),b.date,5), convert(varchar(50),b.usedsum), convert(varchar(50),b.balance) from bigcert_header a
inner join bigcert b
on a.id = b.id
where tel= {tel})
select id from bigcert_header where tel = {tel}
else select b.wrkordno, convert(varchar(20),b.date,5), convert(varchar(50),b.usedsum), convert(varchar(50),b.balance) from bigcert_header a
inner join bigcert b
on a.id = b.id
where tel= {tel}
order by b.date
"""

def balance(tel):
    return f"""if not exists(
select h.id, h.cust_name, a.balance from (
select id,max(date) as date,min(balance) as balance from bigcert group by id) a

join bigcert_header h on a.id=h.id
where h.tel={tel})
select id, cust_name, certsum from  bigcert_header where tel={tel}
else select h.id, h.cust_name,a.balance from (
select id,max(date) as date,min(balance) as balance from bigcert group by id) a

join bigcert_header h on a.id=h.id
where h.tel={tel}
"""
