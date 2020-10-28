with incidents as (
	select	a.usr_sc as chave_usuario
	,		a.usr_n as usuario
	,		b.incident_id
	,		CASE	WHEN b.TYPE_ENUM = 1 THEN '' 
					WHEN b.TYPE_ENUM = 2 THEN 'P'
					WHEN b.TYPE_ENUM = 3 THEN 'R'
					WHEN b.TYPE_ENUM = 7 THEN 'S'
					WHEN b.TYPE_ENUM = 5 THEN 'D'
					ELSE 'T' 
			END + CAST(b.incident_ref AS NVARCHAR(254)) 	AS id_chamado
	,		convert(varchar, b.date_logged, 120) as data_abertura
	,		convert(varchar, b.inc_resolve_act, 120) as data_fechamento
	,		CASE 	WHEN b.STATUS_ENUM = 1 THEN 'Aberto'
					WHEN b.STATUS_ENUM = 2 THEN 'Fechado'
					WHEN b.STATUS_ENUM = 3 THEN 'Resolvido'
					ELSE 'Enviado'
			END 											AS status_evento
	,		b.short_desc as resumo	
	,		TRANSLATE(c.remarks, '"'+CHAR(9)+CHAR(10)+CHAR(13), '    ') as descricao	
	from	usr as a
			--
			inner join vw_incident as b
			on	a.usr_id = b.usr_id
			or	a.usr_id = b.rep_usr_id
			--
			inner join inc_data as c
			on	b.incident_id = c.incident_id 
			--
	where	a.usr_sc in ('R3JA', 'RCGV', 'R3MN', 'C1E4', 'KIJ1', 'CQ48', 'XV43', 'REZ1', 'R3TA', 'XV5P', 'XV4I', 'R3BG', 'XV4K', 'AFGN', 'XV0G')		
	and		b.date_logged >= (CURRENT_TIMESTAMP  - (365/2))
),
last_assignments as (
	select	a.incident_id
	,		max(b.act_reg_id) as last_assignment_id
	from	incidents as a
			--
			inner join vw_act_reg as b
			on 	a.incident_id = b.incident_id
			--and	b.act_type_id = 1 -- 1	ASSIGN	Atribuição interna
			and	b.ass_svd_id <> 0
	group	by a.incident_id
),
last_resolves as (
	select	a.incident_id
	,		max(b.act_reg_id) as last_resolve_id
	from	incidents as a
			--
			inner join vw_act_reg as b
			on 	a.incident_id = b.incident_id
			and	b.act_type_id = 4 -- 4	PENDING-CLOSURE	Resolver
			and	b.ass_svd_id <> 0
	group	by a.incident_id
)
select 	a.chave_usuario
,		a.usuario
,		a.id_chamado
,		a.data_abertura
,		a.data_fechamento
,		a.status_evento
,		f.serv_dept_n as ultima_mesa
,		a.resumo
,		a.descricao
,		TRANSLATE(d.remarks, '"'+CHAR(9)+CHAR(10)+CHAR(13), '    ') as resolucao
from	incidents as a
		--
		left outer join last_resolves as b
		on a.incident_id = b.incident_id
		--
		left outer join last_assignments as c
		on a.incident_id = c.incident_id
		--
		left outer join vw_act_reg as d
		on	b.incident_id = d.incident_id
		and	b.last_resolve_id = d.act_reg_id
		--
		left outer join vw_act_reg as e
		on	b.incident_id = e.incident_id
		and	c.last_assignment_id = e.act_reg_id
		--
		left outer join serv_dept as f
		on e.ass_svd_id = f.serv_dept_id
		--
--where	a.id_chamado not like 'T%'
order	by a.chave_usuario
,		a.id_chamado