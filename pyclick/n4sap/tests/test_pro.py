import unittest
from pyclick.models import *
from pyclick.n4sap.pro import Pro

class TestPro(unittest.TestCase):
    
    def setUp(self):
        self.click = Click()
        self.start_dt = '2020-04-26 00:00:00'
        self.end_dt = '2020-05-26 00:00:00'
        self.pro = Pro()
        self.closed_inc_evts = Event.parse_events(r"""
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8117232	Atribuição interna	N	N1-SD2_EMAIL	2020-04-28 23:32:02	2020-04-28 23:32:02	0
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8117233	Atribuir ao Fornecedor	N	N1-SD2_EMAIL	2020-04-28 23:32:02	2020-04-28 23:39:05	7
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8117285	Item alterado	N	N1-SD2_EMAIL	2020-04-28 23:39:05	2020-04-28 23:39:58	0
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8117288	Atribuição interna	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-04-28 23:39:58	2020-04-28 23:39:58	0
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8117290	Atribuir ao Fornecedor	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-04-28 23:39:58	2020-04-28 23:43:06	4
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8117312	Atribuição interna	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-04-28 23:43:06	2020-04-28 23:44:03	1
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8117341	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-28 23:44:03	2020-04-28 23:44:03	0
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8117343	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-04-28 23:44:03	2020-04-29 06:47:59	0
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8119609	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-29 06:47:59	2020-04-29 07:04:27	4
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8119816	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-29 07:04:27	2020-04-29 07:04:27	0
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8119818	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-29 07:04:27	2020-04-29 08:38:00	0
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8126633	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-29 08:38:00	2020-04-29 09:39:41	39
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8135853	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-29 09:39:41	2020-05-04 10:56:41	1157
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8407236	Resolver	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-04 10:56:41	2020-05-06 10:58:02	0
            447752		ORIENTAR	Dúvida sobre o serviço	99960	8610295	Encerrar	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-06 10:58:02		0
        """)

        self.solved_inc_events = Event.parse_events(r"""
            359390		ORIENTAR	Suporte aos serviços	540	6510801	Atribuição interna	N	N1-SD2_WEB	2020-04-07 14:44:08	2020-04-07 14:44:08	0
            359390		ORIENTAR	Suporte aos serviços	540	6510804	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-04-07 14:44:08	2020-04-07 14:44:11	0
            359390		ORIENTAR	Suporte aos serviços	540	6510806	Campo do formulário alterado	N	N1-SD2_WEB	2020-04-07 14:44:11	2020-04-07 14:49:03	5
            359390		ORIENTAR	Suporte aos serviços	540	6511699	Atribuição interna	N	N1-SD2_WEB	2020-04-07 14:49:03	2020-04-07 14:56:04	7
            359390		ORIENTAR	Suporte aos serviços	540	6513370	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-04-07 14:56:04	2020-04-07 14:56:04	0
            359390		ORIENTAR	Suporte aos serviços	540	6513374	Atribuir ao Fornecedor	N	N2-SD2_SAP_ABGE	2020-04-07 14:56:04	2020-04-07 15:05:20	9
            359390		ORIENTAR	Suporte aos serviços	540	6515338	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-04-07 15:05:20	2020-04-07 15:18:03	13
            359390		ORIENTAR	Suporte aos serviços	540	6518168	Aguardando Cliente	N	N2-SD2_SAP_ABGE	2020-04-07 15:18:03	2020-04-07 15:18:03	0
            359390		ORIENTAR	Suporte aos serviços	540	6518170	Aguardando Cliente - Fornecedor	S	N2-SD2_SAP_ABGE	2020-04-07 15:18:03	2020-04-08 17:59:14	881
            359390		ORIENTAR	Suporte aos serviços	540	6653434	Retorno do usuário	S	N2-SD2_SAP_ABGE	2020-04-08 17:59:14	2020-04-08 17:59:14	0
            359390		ORIENTAR	Suporte aos serviços	540	6653436	Pendência Sanada	S	N2-SD2_SAP_ABGE	2020-04-08 17:59:14	2020-04-08 17:59:15	0
            359390		ORIENTAR	Suporte aos serviços	540	6653438	Pendência Sanada - Fornecedor/TIC	N	N2-SD2_SAP_ABGE	2020-04-08 17:59:15	2020-04-09 09:22:01	203
            359390		ORIENTAR	Suporte aos serviços	540	6686815	Aguardando Cliente	N	N2-SD2_SAP_ABGE	2020-04-09 09:22:01	2020-04-09 09:22:02	0
            359390		ORIENTAR	Suporte aos serviços	540	6686818	Aguardando Cliente - Fornecedor	S	N2-SD2_SAP_ABGE	2020-04-09 09:22:02	2020-04-09 12:46:56	204
            359390		ORIENTAR	Suporte aos serviços	540	6721740	Retorno do usuário	S	N2-SD2_SAP_ABGE	2020-04-09 12:46:56	2020-04-09 12:46:56	0
            359390		ORIENTAR	Suporte aos serviços	540	6721741	Pendência Sanada	S	N2-SD2_SAP_ABGE	2020-04-09 12:46:56	2020-04-09 12:46:57	0
            359390		ORIENTAR	Suporte aos serviços	540	6721742	Pendência Sanada - Fornecedor/TIC	N	N2-SD2_SAP_ABGE	2020-04-09 12:46:57	2020-04-09 13:35:34	49
            359390		ORIENTAR	Suporte aos serviços	540	6726677	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-09 13:35:34	2020-04-09 13:35:34	0
            359390		ORIENTAR	Suporte aos serviços	540	6726681	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-09 13:35:34	2020-04-09 13:38:32	3
            359390		ORIENTAR	Suporte aos serviços	540	6727015	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-09 13:38:32	2020-04-09 14:53:51	75
            359390		ORIENTAR	Suporte aos serviços	540	6738396	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-09 14:53:51	2020-04-13 10:11:13	258
            359390		ORIENTAR	Suporte aos serviços	540	6919339	Pendência de TIC	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-13 10:11:13	2020-04-28 11:48:14	5497
            359390		ORIENTAR	Suporte aos serviços	540	8059491	Resolver	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-28 11:48:14		0
        """)
        
        self.violated_closed_inc_evts = Event.parse_events(r"""
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5886561	Atribuição interna	N	N1-SD2_CHAT_HUMANO	2020-03-31 15:36:54	2020-03-31 15:36:54	0
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5886564	Atribuir ao Fornecedor	N	N1-SD2_CHAT_HUMANO	2020-03-31 15:36:54	2020-03-31 16:28:32	52
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5894745	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-03-31 16:28:32	2020-03-31 16:28:32	0
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5894747	Atribuir ao Fornecedor	N	N2-SD2_SAP_ABGE	2020-03-31 16:28:32	2020-03-31 16:38:05	10
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5896103	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-03-31 16:38:05	2020-03-31 17:01:06	23
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5898932	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-03-31 17:01:06	2020-03-31 17:12:15	11
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5900462	Atribuição interna	N	N2-SD2_CONTROLE_DE_DESVIOS	2020-03-31 17:12:15	2020-03-31 17:12:41	0
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5900499	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-31 17:12:41	2020-03-31 17:12:41	0
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5900503	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-31 17:12:41	2020-03-31 17:15:31	3
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5900792	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-31 17:15:31	2020-03-31 18:16:08	45
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5906120	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-31 18:16:08	2020-04-01 08:28:32	0
            326540		ORIENTAR	Dúvida sobre o serviço	99960	5929919	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-01 08:28:32	2020-04-30 11:52:47	10432
            326540		ORIENTAR	Dúvida sobre o serviço	99960	8258857	Resolver	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-30 11:52:47		0
        """)
        
        self.violated_solved_inc_events = Event.parse_events(r"""
            440047		ORIENTAR	Dúvida sobre o serviço	99960	7992619	Atribuição interna	N	N1-SD2_CHAT_HUMANO	2020-04-27 15:48:02	2020-04-27 15:48:02	0
            440047		ORIENTAR	Dúvida sobre o serviço	99960	7992620	Atribuir ao Fornecedor	N	N1-SD2_CHAT_HUMANO	2020-04-27 15:48:02	2020-04-27 16:26:17	38
            440047		ORIENTAR	Dúvida sobre o serviço	99960	7999386	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-27 16:26:17	2020-04-27 16:26:17	0
            440047		ORIENTAR	Dúvida sobre o serviço	99960	7999389	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-04-27 16:26:17	2020-04-27 16:35:11	9
            440047		ORIENTAR	Dúvida sobre o serviço	99960	8000850	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-27 16:35:11	2020-04-27 17:15:50	40
            440047		ORIENTAR	Dúvida sobre o serviço	99960	8006442	Atribuição interna	N	N2-SD2_CONTROLE_DE_DESVIOS	2020-04-27 17:15:50	2020-04-27 17:18:35	3
            440047		ORIENTAR	Dúvida sobre o serviço	99960	8006673	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-27 17:18:35	2020-04-27 17:18:35	0
            440047		ORIENTAR	Dúvida sobre o serviço	99960	8006675	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-27 17:18:35	2020-04-27 17:42:57	24
            440047		ORIENTAR	Dúvida sobre o serviço	99960	8009069	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-27 17:42:57	2020-05-05 16:17:35	2615
            440047		ORIENTAR	Dúvida sobre o serviço	99960	8558371	Resolver	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-05 16:17:35		0
        """)

        self.cancelled_inc_events = Event.parse_events(r"""
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9627205	Atribuição interna	N	N2-SD2_SAP_CORP	2020-05-19 15:23:07	2020-05-19 15:23:07	0
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9627206	Atribuir ao Fornecedor	N	N2-SD2_SAP_CORP	2020-05-19 15:23:07	2020-05-19 15:30:48	7
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9628523	Atribuição interna	N	N2-SD2_SAP_CORP	2020-05-19 15:30:48	2020-05-19 15:50:28	20
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9632042	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-19 15:50:28	2020-05-19 15:50:28	0
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9632044	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-19 15:50:28	2020-05-19 16:08:21	18
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9635274	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-19 16:08:21	2020-05-20 13:33:51	385
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9711724	Item alterado	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-20 13:33:51	2020-05-20 13:34:51	1
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9711921	Cancelar	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-20 13:34:51	2020-05-20 13:34:56	0
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9711929	Encerrar	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-20 13:34:56	2020-05-20 13:35:06	0
            541500		ORIENTAR	Dúvida sobre o serviço	99960	9711953	Cancelado	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-20 13:35:06		0
        """)

        self.violated_cancelled_inc_events = Event.parse_events(r"""
            406770		ORIENTAR	Suporte aos serviços	540	7429626	Atribuição interna	N	N1-SD2_WEB	2020-04-17 16:47:32	2020-04-17 16:47:32	0
            406770		ORIENTAR	Suporte aos serviços	540	7429629	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-04-17 16:47:32	2020-04-17 16:47:35	0
            406770		ORIENTAR	Suporte aos serviços	540	7429632	Campo do formulário alterado	N	N1-SD2_WEB	2020-04-17 16:47:35	2020-04-17 16:50:05	3
            406770		ORIENTAR	Suporte aos serviços	540	7429984	Atribuição interna	N	N1-SD2_WEB	2020-04-17 16:50:05	2020-04-17 16:56:57	6
            406770		ORIENTAR	Suporte aos serviços	540	7430906	Atribuição interna	N	N2-SD2_SAP_GRC	2020-04-17 16:56:57	2020-04-17 16:56:57	0
            406770		ORIENTAR	Suporte aos serviços	540	7430911	Atribuir ao Fornecedor	N	N2-SD2_SAP_GRC	2020-04-17 16:56:57	2020-04-17 17:03:18	7
            406770		ORIENTAR	Suporte aos serviços	540	7431769	Atribuição interna	N	N2-SD2_SAP_GRC	2020-04-17 17:03:18	2020-04-17 17:40:45	37
            406770		ORIENTAR	Suporte aos serviços	540	7435724	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-04-17 17:40:45	2020-04-17 17:40:45	0
            406770		ORIENTAR	Suporte aos serviços	540	7435726	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-GRC	2020-04-17 17:40:45	2020-04-17 18:21:33	20
            406770		ORIENTAR	Suporte aos serviços	540	7438583	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-04-17 18:21:33	2020-04-24 10:54:26	1734
            406770		ORIENTAR	Suporte aos serviços	540	7804458	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-GRC	2020-04-24 10:54:26	2020-04-24 10:54:27	0
            406770		ORIENTAR	Suporte aos serviços	540	7804463	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-GRC	2020-04-24 10:54:27	2020-04-29 17:07:37	1993
            406770		ORIENTAR	Suporte aos serviços	540	8202179	Cancelar	S	N4-SAP-SUSTENTACAO-GRC	2020-04-29 17:07:37	2020-04-29 17:07:43	0
            406770		ORIENTAR	Suporte aos serviços	540	8202187	Encerrar	S	N4-SAP-SUSTENTACAO-GRC	2020-04-29 17:07:43	2020-04-29 17:07:52	0
            406770		ORIENTAR	Suporte aos serviços	540	8202203	Cancelado	S	N4-SAP-SUSTENTACAO-GRC	2020-04-29 17:07:52		0
        """)

        self.prioritized_inc_events = Event.parse_events(r"""
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7646918	Atribuição interna	N	N1-SD2_SAP	2020-04-24 11:22:38	2020-04-24 11:22:38	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7646920	Atribuir ao Fornecedor	N	N1-SD2_SAP	2020-04-24 11:22:38	2020-04-24 11:49:58	27
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7652041	Campos alterados	N	N1-SD2_SAP	2020-04-24 11:49:58	2020-04-24 11:50:21	1
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7652111	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-24 11:50:21	2020-04-24 11:50:21	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7652114	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-04-24 11:50:21	2020-04-24 11:58:20	8
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7653318	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-24 11:58:20	2020-04-24 12:00:17	2
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7653676	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 12:00:17	2020-04-24 12:00:17	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7653678	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 12:00:17	2020-04-24 12:05:20	5
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7654458	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 12:05:20	2020-04-26 10:07:55	962
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7796121	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 10:07:55	2020-04-26 10:07:55	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7796123	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 10:07:55	2020-04-26 10:08:17	1
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7796186	Campos alterados	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 10:08:17	2020-04-26 15:01:29	293
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7838004	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 15:01:29	2020-04-26 15:01:30	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7838006	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 15:01:30	2020-04-26 17:15:41	134
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7859928	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 17:15:41	2020-04-26 17:15:42	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7859930	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 17:15:42	2020-04-26 17:19:11	4
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7860239	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-26 17:19:11	2020-04-26 17:19:11	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7860242	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-26 17:19:11	2020-04-26 17:25:14	6
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7860887	Item alterado	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-26 17:25:14	2020-04-26 17:25:59	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7860959	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 17:25:59	2020-04-26 17:25:59	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7860961	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 17:25:59	2020-04-26 17:46:09	21
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7862912	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 17:46:09	2020-04-26 19:41:02	115
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7868113	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 19:41:02	2020-04-26 19:41:02	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7868114	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-26 19:41:02	2020-04-29 07:52:26	3611
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7918162	Retorno do usuário	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 07:52:26	2020-04-29 07:52:27	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7918165	Pendência Sanada	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 07:52:27	2020-04-29 07:52:28	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7918166	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 07:52:28	2020-04-29 10:11:33	139
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7939112	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 10:11:33	2020-04-29 14:25:54	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7978189	Reabrir	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 14:25:54	2020-04-29 14:25:54	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7978190	Reaberto pelo Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 14:25:54	2020-04-29 15:27:04	62
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	7989155	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 15:27:04	2020-05-01 16:33:16	0
            418572		ORIENTAR-PESO35	Suporte ao serviço de SAP	540	8197552	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-01 16:33:16		0
        """)

        self.violated_prioritized_inc_events = Event.parse_events(r"""
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9152344	Atribuição interna	N	N1-SD2_WEB	2020-05-13 11:10:05	2020-05-13 11:10:05	0
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9152347	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-05-13 11:10:05	2020-05-13 11:10:08	0
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9152348	Campo do formulário alterado	N	N1-SD2_WEB	2020-05-13 11:10:08	2020-05-13 11:16:56	6
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9153606	Atribuição interna	N	N1-SD2_WEB	2020-05-13 11:16:56	2020-05-13 11:24:22	8
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9155044	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-13 11:24:22	2020-05-13 11:24:22	0
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9155049	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-13 11:24:22	2020-05-13 11:41:30	17
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9157615	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-13 11:41:30	2020-05-13 11:53:49	1200
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9159583	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-13 11:53:49	2020-05-14 12:09:26	556
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9261905	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-14 12:09:26	2020-05-14 12:09:26	0
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9261908	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-14 12:09:26	2020-05-14 12:23:22	14
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9263748	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-14 12:23:22	2020-05-14 12:23:22	0
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9263750	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-14 12:23:22	2020-05-14 12:26:17	3
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9264005	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-14 12:26:17	2020-05-18 08:47:35	5541
            513116		ORIENTAR	Suporte ao serviço de SAP	540	9461480	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-18 08:47:35		10992
        """)
        
        self.forwarded_inc_events = Event.parse_events("""
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8103801	Atribuição interna	N	N1-SD2_CHAT_HUMANO	2020-04-28 17:06:23	2020-04-28 17:06:23	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8103803	Atribuir ao Fornecedor	N	N1-SD2_CHAT_HUMANO	2020-04-28 17:06:23	2020-04-28 17:08:18	2
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8104012	Campos alterados	N	N1-SD2_CHAT_HUMANO	2020-04-28 17:08:18	2020-04-28 17:11:11	3
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8104375	Atribuição interna	N	N4-SAP-SUSTENTACAO-CE	2020-04-28 17:11:11	2020-04-28 17:11:11	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8104378	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CE	2020-04-28 17:11:11	2020-04-28 17:14:03	3
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8104730	Atribuição interna	N	N4-SAP-SUSTENTACAO-CE	2020-04-28 17:14:03	2020-04-28 17:14:14	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8104756	Atribuição interna	N	N4-SAP-SUSTENTACAO-CE	2020-04-28 17:14:14	2020-05-04 10:02:20	1368
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8396229	Atribuição interna	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 10:02:20	2020-05-04 10:02:20	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8396231	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 10:02:20	2020-05-04 10:18:10	16
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8399315	Atribuição interna	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 10:18:10	2020-05-04 10:23:41	5
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8400406	Atribuição interna	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 10:23:41	2020-05-04 12:30:01	127
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8424291	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 12:30:01	2020-05-04 12:30:02	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8424292	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-04 12:30:02	2020-05-07 14:42:11	1752
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8744122	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-07 14:42:11	2020-05-07 14:42:11	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	8744124	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-07 14:42:11	2020-05-12 10:15:38	1353
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9045661	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-12 10:15:38	2020-05-12 10:15:39	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9045663	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-12 10:15:39	2020-05-13 10:25:42	550
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9144417	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-13 10:25:42	2020-05-13 10:25:43	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9144422	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-13 10:25:43	2020-05-13 10:30:47	5
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9145138	Atribuição interna	N	N4-SAP-SUSTENTACAO-CE	2020-05-13 10:30:47	2020-05-13 10:30:47	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9145141	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CE	2020-05-13 10:30:47	2020-05-13 10:34:55	4
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9145805	Atribuição interna	N	N4-SAP-SUSTENTACAO-CE	2020-05-13 10:34:55	2020-05-13 13:01:59	147
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9168069	Atribuição interna	N	N4-SAP-SUSTENTACAO-CE	2020-05-13 13:01:59	2020-05-13 14:00:30	59
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9174313	Resolver	N	N4-SAP-SUSTENTACAO-CE	2020-05-13 14:00:30	2020-05-15 14:03:00	0
            446932		ORIENTAR-PESO35	Dúvida sobre o serviço	99960	9369950	Encerrar	N	N4-SAP-SUSTENTACAO-CE	2020-05-15 14:03:00		0        
        """)
        
        self.violated_forwarded_inc_events = Event.parse_events("""            
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8595987	Atribuição interna	N	N1-SD2_EMAIL	2020-05-06 09:38:30	2020-05-06 09:38:30	0
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8595992	Atribuir ao Fornecedor	N	N1-SD2_EMAIL	2020-05-06 09:38:30	2020-05-06 09:39:01	1
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8596052	Atribuição interna	N	N2-SD2_SAP_SERV	2020-05-06 09:39:01	2020-05-06 09:39:01	0
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8596054	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-05-06 09:39:01	2020-05-06 09:44:51	5
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8597139	Atribuição interna	N	N2-SD2_SAP_SERV	2020-05-06 09:44:51	2020-05-06 10:21:03	37
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8603522	Reabrir	N	N2-SD2_SAP_SERV	2020-05-06 10:21:03	2020-05-06 10:21:03	0
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8603523	Reaberto pelo Fornecedor	N	N2-SD2_SAP_SERV	2020-05-06 10:21:03	2020-05-06 12:39:56	138
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8626891	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-06 12:39:56	2020-05-06 12:39:56	0
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8626893	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-06 12:39:56	2020-05-06 12:48:01	9
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8627750	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-06 12:48:01	2020-05-08 17:03:40	1335
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8867170	Atribuição interna	N	N4-SAP-SUSTENTACAO-SATI	2020-05-08 17:03:40	2020-05-08 17:03:40	0
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8867173	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SATI	2020-05-08 17:03:40	2020-05-08 18:13:32	57
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8873966	Atribuição interna	N	N2-SD2_CONTROLE_DE_DESVIOS	2020-05-08 18:13:32	2020-05-08 18:13:32	0
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8873968	Atribuir ao Fornecedor	N	N2-SD2_CONTROLE_DE_DESVIOS	2020-05-08 18:13:32	2020-05-11 12:37:12	384
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8966451	Atribuição interna	N	N2-SD2_CONTROLE_DE_DESVIOS	2020-05-11 12:37:12	2020-05-11 13:08:37	31
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8969111	Atribuição interna	N	N2-SD2_SAP_SERV	2020-05-11 13:08:37	2020-05-11 13:11:03	3
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8969349	Atribuição interna	N	N2-SD2_SAP_SERV	2020-05-11 13:11:03	2020-05-11 13:47:13	36
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8973239	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-11 13:47:13	2020-05-11 13:47:13	0
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8973241	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-11 13:47:13	2020-05-11 14:25:10	38
            477878		ORIENTAR	Dúvida sobre o serviço	99960	8978684	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-11 14:25:10	2020-05-12 16:06:51	641
            477878		ORIENTAR	Dúvida sobre o serviço	99960	9098485	Atribuição interna	N	N4-ATEND_DESENVOLV-SBSTRIB	2020-05-12 16:06:51	2020-05-12 16:06:51	0
            477878		ORIENTAR	Dúvida sobre o serviço	99960	9098491	Atribuir ao Fornecedor	N	N4-ATEND_DESENVOLV-SBSTRIB	2020-05-12 16:06:51		19193
        """)
    
        self.events = self.closed_inc_evts                 \
        +             self.violated_closed_inc_evts        \
        +             self.solved_inc_events               \
        +             self.violated_solved_inc_events      \
        +             self.cancelled_inc_events            \
        +             self.violated_cancelled_inc_events   \
        +             self.prioritized_inc_events          \
        +             self.violated_prioritized_inc_events \
        +             self.forwarded_inc_events            \
        +             self.violated_forwarded_inc_events        
        
    def tearDown(self):
        pass
    
    def test_it_computes_the_kpi_for_no_incidents(self):
        kpi, observation = self.pro.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente orientar processado", observation)
    
    def test_it_computes_the_kpi_for_a_closed_incident(self):
        for evt in self.closed_inc_evts:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)

    def test_it_computes_the_kpi_for_a_closed_incident_that_violated_the_sla(self):
        for evt in self.violated_closed_inc_evts:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
        
    def test_it_computes_the_kpi_for_solved_inc_events(self):
        for evt in self.solved_inc_events:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)

    def test_it_computes_the_kpi_for_solved_inc_events_that_violated_the_sla(self):
        for evt in self.violated_solved_inc_events:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)

    def test_it_computes_the_kpi_for_cancelles_inc_events(self):
        for evt in self.cancelled_inc_events:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)

    def test_it_computes_the_kpi_for_cancelles_inc_events_that_violated_the_sla(self):
        for evt in self.violated_cancelled_inc_events:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)

    def test_it_compute_the_kpi_for_prioritized_inc_events(self):
        for evt in self.prioritized_inc_events:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)

    def test_it_compute_the_kpi_for_prioritized_inc_events_that_violated_the_sla(self):
        for evt in self.violated_prioritized_inc_events:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_compute_the_kpi_for_forwarded_inc_events(self):
        for evt in self.forwarded_inc_events:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
    
    def test_it_compute_the_kpi_for_forwarded_inc_events_that_violated_the_sla(self):
        for evt in self.violated_forwarded_inc_events:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    

    def test_it_computes_the_kpi(self):
        for evt in self.events:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(50.0, kpi)
        self.assertEqual("5 violações / 10 incidentes", observation)
        #self.pro.get_details().to_excel("teste.xlsx")

    def test_it_skips_incs_with_prior_assignments_and_no_current_assigment(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-24 23:59:59	0        
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente orientar processado", observation)

    def test_it_considers_incs_with_prior_assignments_closed_within_period(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	0
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-26 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.pro.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.pro.get_result()
        self.assertEqual(0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
        