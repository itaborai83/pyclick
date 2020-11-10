with ultima_acao_n4 as (
	select	a.id_chamado
	,		max(a.id_acao) as max_id_acao
	from	incidente_acoes as a
	where	a.mesa_atual in (select mesa from mesas)
	group	by a.id_chamado
	order	by a.id_chamado
),
texts as (
	select	id_chamado
	,		group_concat(replace(printf('%.' || freq || 'c', '/'),'/', termo || ' '), ' ') as texto
	from	incidente_termos
	group	by id_chamado
	order	by id_chamado 
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
select	a.ultimo_designado_n4 as designado
,		sum(case when a.status = 'Aberto' and a.n4 = 'S'			then 1 		else 0 end) as incidentes_abertos
,		group_concat(case when a.n4 = 'S' and a.status = 'Fechado' 	then texto 	else '' end, ' ') as texto_fechados
,		group_concat(case when a.n4 = 'S' and a.status = 'Aberto' 	then texto 	else '' end, ' ') as texto_abertos
from	incidents as a
		--
		inner join texts as b
		on	a.id_chamado = b.id_chamado
		--
where	a.ultimo_designado_n4 is not null
group	by a.ultimo_designado_n4
order	by 2 desc