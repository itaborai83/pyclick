with incs as (
	select	a.id_chamado
	,		case when a.data_resolucao_chamado is null then 'ABERTO' else 'FECHADO' end as status
	,		b.mesa
	,       cast(
				julianday( coalesce(a.data_resolucao_chamado, (select valor from params where param = 'HORA_FIM_APURACAO')) ) 
			- 	julianday(a.data_abertura_chamado) as integer
			) as aging
	from	incidentes as a
			--
			inner join incidente_acoes as b
			on	a.id_chamado = b.id_chamado
			and	b.mesa_atual in (select mesa from mesas)
			and	b.ultima_acao = 'y'
			--
	where	a.id_chamado not like 'S%'
	order	by 4 desc -- aging
	,		a.id_chamado
),
data as (
	select	a.id_chamado
	,		a.status
	,		a.mesa
	,       a.aging
	,		case 	when a.aging < 60 then 'ok' 
					else 'aging 60+'
			end as categoria
	,		c.termo
	,		c.freq
	from	incs as a
			--
			inner join incidente_termos as c
			on	a.id_chamado = c.id_chamado
			--
	where	a.id_chamado not like 'S%'
	order	by a.aging desc
	,		a.id_chamado
	,		c.freq desc
	,		c.termo
) 
select	id_chamado
,		status
,		mesa
,		aging
,		categoria
-- https://stackoverflow.com/questions/11568496/how-to-emulate-repeat-in-sqlite 
-- what an ugly hack!!!
,		replace(printf('%.' || max(freq) || 'c', '/'),'/', mesa || ' ') || ' ' ||
		group_concat(replace(printf('%.' || freq || 'c', '/'),'/', termo || ' '), '') as texto  
from	data
group	by id_chamado
,		status
,		mesa
,		aging
,		categoria
order	by id_chamado
,		status
,		mesa
,		aging
,		categoria