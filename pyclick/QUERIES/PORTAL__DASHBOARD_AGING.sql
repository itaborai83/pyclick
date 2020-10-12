-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- Data Fim
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
WITH data_fim as (
    select  min(cast(julianday(valor) as integer), cast(julianday('now') as integer) ) as valor
    from    PARAMS p 
    where   param = 'HORA_FIM_APURACAO'
),
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- Incidentes Abertos
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
incidentes_abertos as (
    select  a.*
    ,       b.mesa_atual
    ,       b.data_inicio_acao as data_ultima_acao
    from    incidentes as a
            --
            inner join incidente_acoes as b
            on  a.id_chamado    = b.id_chamado
            and b.ultima_acao   = 'y'
            and b.mesa_atual    in (select mesa from mesas)
    where   1=1
    and     a.status_de_evento  = 'Aberto'
    and     a.id_chamado        not like 'S%'
    order   by a.id_chamado
    ,       b.mesa_atual
),
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- Desginados
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
ultimas_designacoes as (
    select  a.id_chamado
    ,   max(b.id_acao) as max_id_acao
    from    incidentes_abertos as a
            --
            inner join incidente_acoes as b
            on  a.id_chamado        = b.id_chamado
            and b.designado         is not null
            --
    group   by a.id_chamado
    order   by a.id_chamado
),
designados as (
    select  a.id_chamado
    ,       b.designado
    from    ultimas_designacoes as a
            --
            inner join incidente_acoes as b
            on  a.id_chamado        = b.id_chamado
            and a.max_id_acao       = b.id_acao
            --
    order   by a.id_chamado
),
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- Durações & Pendencias
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
duracoes as (
    select  a.id_chamado
    ,       sum(case when pendencia = 'N' then b.duracao_m else 0 end) as duration_m
    ,       sum(case when pendencia = 'S' then b.duracao_m else 0 end) as pending_m
    from    incidentes_abertos as a
            --
            inner join INCIDENTE_ACOES as b
            on 	a.id_chamado        = b.id_chamado
            and a.mesa_atual        = b.mesa_atual
    where   a.mesa_atual            <> 'N4-SAP-SUSTENTACAO-PRIORIDADE'
    group   by a.id_chamado
    -- 
    union all
    ---
    select  a.id_chamado
    ,       sum(case when pendencia = 'N' then b.duracao_m else 0 end) as duration_m
    ,       sum(case when pendencia = 'S' then b.duracao_m else 0 end) as pending_m
    from    incidentes_abertos as a
            --
            inner join INCIDENTE_ACOES as b
            on 	a.id_chamado        = b.id_chamado
            and a.mesa_atual        = b.mesa_atual
    where   a.mesa_atual            = 'N4-SAP-SUSTENTACAO-PRIORIDADE'
    --
    group   by a.id_chamado
    order   by a.id_chamado	
),
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- Query Prinicipal
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
entradas_n4 as (
    select  a.id_chamado
    ,       min(b.data_inicio_acao) as data_entrada_n4
    from    incidentes_abertos as a
            -- 
            inner join incidente_acoes as b
            on  a.id_chamado = b.id_chamado
            and b.mesa_atual in (select mesa from mesas)
            --
    group   by a.id_chamado
)
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
--
-- Query Prinicipal
--
-------------------------------------------------------------------------------
-------------------------------------------------------------------------------
select  a.id_chamado                                                                                    as incident_id
,       a.chamado_pai                                                                                   as parent_id
,       c.mesa_atual                                                                                    as group_
,       case    when a.id_chamado like 'T%'         then 'ATENDER'
                when categoria    like '%CORRIGIR%' then 'CORRIGIR'
                                                    else 'ORIENTAR'
        end                                                                                             as category
,       case    when c.PENDENCIA = 'S' then 'Y' 
                when c.PENDENCIA = 'N' then 'N'
                else '???'
        end                                                                                             as pending
,       data_abertura_chamado                                                                           as created_at
,       c.ultima_acao_nome                                                                              as last_action
,       c.data_inicio_acao                                                                              as last_action_date
,       d.designado                                                                                     as handler_name
,       b.usuario_afetado                                                                               as client
,       b.nome_do_usuario_afetado                                                                       as client_name
,       b.departamento_cliente                                                                          as orgunit
,       e.duration_m                                                                                    as duration_m
,       e.pending_m                                                                                     as pending_m
,       cast(julianday( (select valor from data_fim) ) - julianday(a.data_abertura_chamado) as integer) as aging
,       cast(julianday( (select valor from data_fim) ) - julianday(f.data_entrada_n4)       as integer) as aging_n4
,       cast(julianday( (select valor from data_fim) ) - julianday(a.data_ultima_acao)      as integer) as aging_last_action
from    incidentes_abertos as a
        --
        inner join incidente_solicitantes as b
        on 	a.id_chamado    = b.id_chamado
        --
        inner join incidente_acoes as c
        on 	a.id_chamado    = c.id_chamado
        and	c.ultima_acao   = 'y'
        and	c.mesa_atual    in (select mesa from mesas)
        --
        left outer join designados as d
        on 	a.id_chamado = d.id_chamado
        --
        left outer join duracoes as e
        on 	a.id_chamado = e.id_chamado
        --
        left outer join entradas_n4 as f
        on 	a.id_chamado = f.id_chamado
        --
where   a.status_de_evento not in ('Fechado', 'Resolvido')
and     a.id_chamado not like 'S%'
order   by 1
