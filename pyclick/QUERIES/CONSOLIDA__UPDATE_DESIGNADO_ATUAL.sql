with atribuicoes as (
	select	a.id_chamado
	,		a.id_acao
	,		lead(a.id_acao) over (partition by a.id_chamado order by a.id_acao) as prox_atrib
	,		a.mesa
	,		a.designado
	from	rel_medicao as a
	where	a.ULTIMA_ACAO_NOME = 'Atribuição interna'
	order	by a.id_chamado
	,		a.id_acao 
),
designados as (
	select	a.id_chamado
	,		a.id_acao
	,		b.mesa
	,		b.designado
	from	rel_medicao as a
			--
			left outer join atribuicoes as b
			on 	a.id_chamado = b.id_chamado
			and	a.id_acao >= b.id_acao
			and	a.id_acao < coalesce(b.prox_atrib, 9999999999999)
	group	by a.id_chamado
	,		a.id_acao
)
update	rel_medicao as a
set		designado	= ( select designado from designados where id_chamado = a.id_chamado and id_acao = a.id_acao )
,		mesa		= ( select      mesa from designados where id_chamado = a.id_chamado and id_acao = a.id_acao )
where	ULTIMA_ACAO_NOME <> 'Atribuição interna';