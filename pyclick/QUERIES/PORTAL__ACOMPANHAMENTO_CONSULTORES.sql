with ultima_acao_n4 as (
	select	a.id_chamado
	,		max(a.id_acao) as max_id_acao
	from	incidente_acoes as a
	where	a.mesa_atual in (select mesa from mesas)
	group	by a.id_chamado
	order	by a.id_chamado
),
incidents as (
	select	a.id_chamado
	,		case	when a.id_chamado like 'T%' 		then 'ATENDER'
					when a.CATEGORIA like '%CORRIGIR%' 	then 'CORRIGIR'
					else 'ORIENTAR'
			end 							as categoria
	,		a.status_de_evento 				as status
	,		b.mesa 							as ultima_mesa
	,		b.designado 					as ultimo_designado
	,		d.mesa 							as ultima_mesa_n4
	,		d.designado 					as ultimo_designado_n4
	,		cast(
					julianday( coalesce(a.data_resolucao_chamado, (select valor from params where param = 'HORA_FIM_APURACAO')) ) 
				- 	julianday(a.data_abertura_chamado) as integer
			) 							as aging
	,		case 	when b.mesa in (select mesa from mesas) then 'S' 
					else 'N' 
			end 							as n4
	from	incidentes 						as a
			--
			inner join incidente_acoes 		as b
			on	a.id_chamado = b.id_chamado
			and	b.ultima_acao = 'y'
			--
			left outer join ultima_acao_n4 	as c
			on 	a.id_chamado = c.id_chamado
			--
			left outer join incidente_acoes as d
			on	c.id_chamado = d.id_chamado
			and	c.max_id_acao = d.id_acao
			--
	where	a.id_chamado not like 'S%'
	order	by a.data_abertura_chamado desc
)
select	a.ultimo_designado_n4 																				as designado
,		sum(case when a.n4 = 'S' and a.status = 'Fechado' then 1 else 0 end) 
+		sum(case when a.n4 = 'N'                          then 1 else 0 end) 								as fechados
,		sum(case when a.n4 = 'S' and a.status = 'Aberto'  then 1 else 0 end) 								as abertos
		-- AGING ABERTOS --
,		sum(case when a.n4 = 'S' and a.status = 'Aberto' and aging between  0 and 29   	then 1 else 0 end) 	as aging_ok
,		sum(case when a.n4 = 'S' and a.status = 'Aberto' and aging between 30 and 59   	then 1 else 0 end) 	as aging_30
,		sum(case when a.n4 = 'S' and a.status = 'Aberto' and aging between 60 and 89   	then 1 else 0 end) 	as aging_60
,		sum(case when a.n4 = 'S' and a.status = 'Aberto' and aging between 90 and 9999 	then 1 else 0 end) 	as aging_90
		-- CORRIGIR --
,		sum(case when a.categoria = 'CORRIGIR' and a.n4 = 'S' and a.status = 'Fechado' 	then 1 else 0 end)
+		sum(case when a.categoria = 'CORRIGIR' and a.n4 = 'N'                          	then 1 else 0 end) 	as corrigir_fechados
,		sum(case when a.categoria = 'CORRIGIR' and a.n4 = 'S' and a.status = 'Aberto'  	then 1 else 0 end) 	as corrigir_abertos
		-- ORIENTAR -- 
,		sum(case when a.categoria = 'ORIENTAR' and a.n4 = 'S' and a.status = 'Fechado' 	then 1 else 0 end)
+		sum(case when a.categoria = 'ORIENTAR' and a.n4 = 'N' 							then 1 else 0 end) 	as orientar_fechados
,		sum(case when a.categoria = 'ORIENTAR' and a.n4 = 'S' and a.status = 'Aberto' 	then 1 else 0 end) 	as orientar_abertos
		-- ATENDER --
,		sum(case when a.categoria = 'ATENDER' and a.n4 = 'S' and a.status = 'Fechado' 	then 1 else 0 end)
+		sum(case when a.categoria = 'ATENDER' and a.n4 = 'N' 							then 1 else 0 end) 	as atender_fechados
,		sum(case when a.categoria = 'ATENDER' and a.n4 = 'S' and a.status = 'Aberto' 	then 1 else 0 end) 	as atender_abertos
from	incidents as a
where	a.ultimo_designado_n4 is not null
group	by a.ultimo_designado_n4
order	by 1 desc


