WITH texts as (
	select	id_chamado
	,		group_concat(replace(printf('%.' || freq || 'c', '/'),'/', termo || ' '), ' ') as texto
	from	incidente_termos
	group	by id_chamado
	order	by id_chamado 
),
incidents as (
	select	a.id_chamado
	,		a.status_de_evento 				as status
	,		b.mesa 							as ultima_mesa
	from	incidentes 						as a
			--
			inner join incidente_acoes 		as b
			on	a.id_chamado = b.id_chamado
			and	b.ultima_acao = 'y'
			and b.mesa_atual in (select mesa from mesas)
			--
	where	1=1 -- a.id_chamado not like 'S%' -- ??
	order	by a.data_abertura_chamado desc
) 
select	a.ultima_mesa as mesa
,		a.status
,		group_concat(texto, ' ') as textos
from	incidents as a
		--
		inner join texts as b
		on	a.id_chamado = b.id_chamado
		--
group	by a.ultima_mesa
