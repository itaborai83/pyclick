with tempos as(
	select	id_chamado
	,		mesa_atual as mesa
	,		count(*) as qtd_acoes
	,		sum(case when pendencia = 'N' then duracao_m else 0 end) as duracao_m
	,		sum(case when pendencia = 'N' then 0 else duracao_m end) as pendencia_m
	from	incidente_acoes
	where	mesa_atual in (select mesa from mesas)
	group	by 1, 2
	order	by 1, 2
),
designados as (
	select	id_chamado
	,		mesa
	,		group_concat(designado, ', ') as designados
	from	(
				select	distinct id_chamado
				,		mesa_atual as mesa
				,		designado
				from	incidente_acoes
				where	mesa_atual in (select mesa from mesas)
				and		(designado is not null or designado <> '')
				group	by 1, 2, 3
				order	by 1, 2
			) as a
	group	by 1, 2
	order	by 1, 2
),
resolucoes as (
	select	id_chamado
	,		group_concat(RESOLUCAO, '|| NOVA RESOLUCAO || ') as resolucao
	from	incidente_acoes
	where	resolucao is not null
	group	by 1
	order	by 1, 2
)
select	b.ID_CHAMADO 
,		c.CHAMADO_PAI
,		b.mesa_atual as ultima_mesa
,		b.ULTIMA_ACAO_NOME as ultima_acao
,		b.DATA_INICIO_ACAO as dt_ult_acao
,		c.status_de_evento
,		c.categoria
,		c.CATEGORIA_MAIOR 
,		c.OFERTA_CATALOGO 
,		c.PRAZO_OFERTA_M 
,		c.resumo
,		f.resolucao
,		d.mesa
,		d.qtd_acoes
,		d.duracao_m
,		d.pendencia_m
,		e.designados
from	mesas as a
		--
		inner join INCIDENTE_ACOES as b
		on 	a.mesa = b.MESA_ATUAL 
		and b.ULTIMA_ACAO = 'y'
		--
		inner join incidentes as c
		on	b.id_chamado = c.id_chamado
		--
		left outer join resolucoes as f
		on c.ID_CHAMADO = f.id_chamado
		--
		left outer join tempos as d
		on b.id_chamado = d.id_chamado
		--
		left outer join designados as e
		on 	d.id_chamado = e.id_chamado
		and d.mesa = e.mesa
order	by b.ID_CHAMADO 
,		b.mesa_atual
,		d.mesa
