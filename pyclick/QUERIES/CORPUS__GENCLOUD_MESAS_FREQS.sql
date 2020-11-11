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
select	a.ultima_mesa_n4 as mesa
,		a.categoria
,		b.termo
,		sum(b.freq) as freq
from	incidents as a
		--
		inner join incidente_termos as b
		on	a.id_chamado = b.id_chamado
		--
where	a.a.ultima_mesa_n4 is not null
group	by a.ultima_mesa_n4
,		a.categoria
,		b.termo
having	sum(b.freq) >= 10
order	by 1, 2, 3