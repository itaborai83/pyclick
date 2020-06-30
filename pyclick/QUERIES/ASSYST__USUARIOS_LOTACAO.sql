select	a.dept_n
,		b.usr_sc
,		b.usr_n
,		b.email_add 
from	sectn_dept as a
		--
		inner join usr as b
		on a.sectn_dept_id = b.sectn_dept_id
		--
		inner join assyst_usr as c
		on b.usr_sc = c.assyst_usr_sc 
		--
where	dept_n like 'TIC/CORP/DS-SIG/SUST'
order	by 2
