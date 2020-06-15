import unittest
from pyclick.models import *
from pyclick.n4sap.prs import PrsV2

class TestPro(unittest.TestCase):
    
    def setUp(self):
        self.click = Click()
        self.prs = PrsV2()
        self.start_dt = '2020-04-26 00:00:00'
        self.end_dt = '2020-05-26 00:00:00'
        self.closed_inc_evts = Event.parse_events(r"""
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5893881	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-31 16:23:15	2020-03-31 16:23:15	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5893883	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-31 16:23:15	2020-03-31 16:23:36	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5893915	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-31 16:23:36	2020-03-31 16:23:37	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5893918	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-03-31 16:23:37	2020-03-31 16:42:46	19
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5896670	Atribuição interna	S	N4-SAP_DEMANDAS_PS	2020-03-31 16:42:46	2020-03-31 16:42:46	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5896673	Atribuir ao Fornecedor	S	N4-SAP_DEMANDAS_PS	2020-03-31 16:42:46	2020-03-31 17:28:34	18
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	5901944	Pendência Sanada - Aprovação	S	N4-SAP_DEMANDAS_PS	2020-03-31 17:28:34	2020-04-27 11:11:43	8291
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	7950977	Atribuição interna	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 11:11:43	2020-04-27 11:11:43	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	7950980	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 11:11:43	2020-04-27 11:19:04	8
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	7952253	Atribuição interna	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 11:19:04	2020-04-27 15:14:01	235
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	7986870	Resolver	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 15:14:01	2020-04-29 16:35:25	0
            S188668		ATENDER	PS - Cadastro na YSPS_DESCONTAHRS	2700	8198052	Encerrar	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-29 16:35:25		0
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	5901939	Atribuição interna	N	N4-SAP_DEMANDAS_PS	2020-03-31 17:28:28	2020-03-31 17:28:28	0
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	5901940	Atribuir ao Fornecedor	N	N4-SAP_DEMANDAS_PS	2020-03-31 17:28:28	2020-04-27 15:13:57	8533
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	7986863	Resolver	N	N4-SAP_DEMANDAS_PS	2020-04-27 15:13:57	2020-04-27 15:13:57	0
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	7986866	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 15:13:57	2020-04-29 16:35:26	1162
            T327450	S188668	Execução	PS - Cadastro na YSPS_DESCONTAHRS	2700	8198055	Encerrar	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-29 16:35:26		0
        """)

        self.violated_closed_inc_evts = Event.parse_events(r"""
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5021744	Atribuição interna	N	N2-SD2_SAP_GRC	2020-03-20 22:57:18	2020-03-20 22:57:18	0
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5021746	Atribuir ao Fornecedor	N	N2-SD2_SAP_GRC	2020-03-20 22:57:18	2020-03-20 22:57:22	0
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5021747	Campo do formulário alterado	N	N2-SD2_SAP_GRC	2020-03-20 22:57:22	2020-03-23 07:16:04	16
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5148731	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-03-23 07:16:04	2020-03-23 07:25:56	9
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5149095	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-03-23 07:25:56	2020-03-23 07:45:04	20
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5150174	Atribuição interna	N	N2-SD2_CONTROLE_DE_DESVIOS	2020-03-23 07:45:04	2020-03-23 07:45:29	0
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5150197	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-23 07:45:29	2020-03-23 07:45:29	0
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5150200	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-23 07:45:29	2020-03-23 07:50:28	0
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5150494	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-23 07:50:28	2020-03-23 12:30:51	210
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5190809	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-23 12:30:51	2020-03-24 03:13:48	330
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5248768	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-24 03:13:48	2020-03-26 12:18:30	1278
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5501278	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-26 12:18:30	2020-03-26 12:18:31	0
            S166308		ATENDER	Outras Solicitações - Perfis	5400	5501281	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-26 12:18:31	2020-04-20 14:53:51	8795
            S166308		ATENDER	Outras Solicitações - Perfis	5400	7554506	Atribuição interna	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-20 14:53:51	2020-05-19 09:34:06	9941
            S166308		ATENDER	Outras Solicitações - Perfis	5400	9575814	Resolver	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-19 09:34:06	2020-05-21 09:38:13	0
            S166308		ATENDER	Outras Solicitações - Perfis	5400	9773486	Encerrar	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-21 09:38:13		0
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	5021755	Atribuição interna	N	N2-SD2_SAP_GRC	2020-03-20 22:57:27	2020-03-20 22:57:27	0
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	5021756	Atribuir ao Fornecedor	N	N2-SD2_SAP_GRC	2020-03-20 22:57:27	2020-03-23 07:17:11	17
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	5148769	Atribuição interna	N	N2-SD2_SAP_GRC	2020-03-23 07:17:11	2020-03-23 07:17:43	0
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	5148778	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-03-23 07:17:43	2020-03-23 07:25:56	8
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	5149097	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-03-23 07:25:56	2020-03-23 08:42:32	77
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	5155952	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-23 08:42:32	2020-03-23 08:42:32	0
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	5155954	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-23 08:42:32	2020-03-23 12:30:51	210
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	5190815	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-23 12:30:51	2020-03-24 03:14:51	330
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	5248779	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-03-24 03:14:51	2020-05-18 14:42:20	19782
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	9517527	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-18 14:42:20	2020-05-18 14:42:21	0
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	9517535	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-18 14:42:21	2020-05-19 09:29:27	227
            T280847	S166308	Execução	Outras Solicitações - Perfis	5400	9574973	Resolver	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-19 09:29:27		0
        """)
        
        self.solved_inc_events = Event.parse_events(r"""
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	6764143	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-09 17:35:20	2020-04-09 17:35:20	0
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	6764144	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-09 17:35:20	2020-04-09 17:42:06	7
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	6764738	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-09 17:42:06	2020-04-09 17:42:26	0
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	6764762	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-09 17:42:26	2020-04-15 17:32:06	1610
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7220763	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-15 17:32:06	2020-04-15 17:32:07	0
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7220767	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-15 17:32:07	2020-04-17 17:16:09	1064
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7433351	Pendência Sanada	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-17 17:16:09	2020-04-17 17:16:09	0
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7433352	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-17 17:16:09	2020-04-20 11:24:46	188
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7528139	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-20 11:24:46	2020-04-20 11:24:46	0
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7528140	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-20 11:24:46	2020-04-24 11:36:56	1632
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7811698	Pendência Sanada	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-24 11:36:56	2020-04-24 11:36:56	0
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7811702	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-24 11:36:56	2020-04-27 08:55:44	384
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7926200	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 08:55:44	2020-04-27 08:55:44	0
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7926201	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 08:55:44	2020-04-27 09:04:33	4
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7927357	Pendência Sanada	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 09:04:33	2020-04-27 09:04:34	0
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	7927360	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 09:04:34	2020-04-28 16:16:34	972
            S208909		ATENDER	PS - Duplicar e Atualização de dados de JVA	5400	8096029	Resolver	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-28 16:16:34		0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	6764152	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-09 17:35:29	2020-04-09 17:35:29	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	6764153	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-09 17:35:29	2020-04-09 17:42:27	7
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	6764763	Atribuição interna	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-09 17:42:27	2020-04-15 17:32:01	1610
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7220753	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-15 17:32:01	2020-04-15 17:32:02	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7220754	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-15 17:32:02	2020-04-17 17:16:02	1064
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7433339	Retorno do usuário	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-17 17:16:02	2020-04-17 17:16:03	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7433341	Pendência Sanada	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-17 17:16:03	2020-04-17 17:16:04	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7433343	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-17 17:16:04	2020-04-20 11:24:40	188
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7528114	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-20 11:24:40	2020-04-20 11:24:41	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7528119	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-20 11:24:41	2020-04-24 08:59:14	1476
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7784415	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-24 08:59:14	2020-04-24 08:59:15	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7784418	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-24 08:59:15	2020-04-24 09:01:45	1
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7784696	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-24 09:01:45	2020-04-24 09:01:45	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7784697	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-24 09:01:45	2020-04-24 11:36:49	155
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7811687	Pendência Sanada	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-24 11:36:49	2020-04-24 11:36:50	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7811689	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-24 11:36:50	2020-04-27 08:55:37	384
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7926186	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 08:55:37	2020-04-27 08:55:39	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7926187	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 08:55:39	2020-04-27 09:04:25	4
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7927311	Retorno do usuário	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 09:04:25	2020-04-27 09:04:26	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7927314	Pendência Sanada	S	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 09:04:26	2020-04-27 09:04:27	0
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	7927321	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-27 09:04:27	2020-04-28 16:16:33	972
            T372414	S208909	Execução	PS - Duplicar e Atualização de dados de JVA	5400	8096025	Resolver	N	N4-SAP-SUSTENTACAO-APOIO_OPERACAO	2020-04-28 16:16:33		0
        """)
        
        self.violated_solved_inc_events = Event.parse_events(r"""
            S251838		ATENDER	GRC / AC - Outros	5400	8433084	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-05-04 13:54:02	2020-05-04 13:54:02	0
            S251838		ATENDER	GRC / AC - Outros	5400	8433086	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-GRC	2020-05-04 13:54:02	2020-05-04 13:54:06	0
            S251838		ATENDER	GRC / AC - Outros	5400	8433088	Campo do formulário alterado	N	N4-SAP-SUSTENTACAO-GRC	2020-05-04 13:54:06	2020-05-04 14:07:58	13
            S251838		ATENDER	GRC / AC - Outros	5400	8434915	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-05-04 14:07:58	2020-05-18 17:43:49	5616
            S251838		ATENDER	GRC / AC - Outros	5400	9543077	Resolver	N	N4-SAP-SUSTENTACAO-GRC	2020-05-18 17:43:49		0
            T467301	S251838	Execução	GRC / AC - Outros	5400	8433106	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-05-04 13:54:13	2020-05-04 13:54:13	0
            T467301	S251838	Execução	GRC / AC - Outros	5400	8433108	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-GRC	2020-05-04 13:54:13	2020-05-04 14:09:43	15
            T467301	S251838	Execução	GRC / AC - Outros	5400	8435129	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-05-04 14:09:43	2020-05-18 17:43:47	5614
            T467301	S251838	Execução	GRC / AC - Outros	5400	9543074	Resolver	N	N4-SAP-SUSTENTACAO-GRC	2020-05-18 17:43:47		0
        """)
        
        self.cancelled_inc_events = Event.parse_events(r"""
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	7196688	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-15 14:51:53	2020-04-15 14:51:53	0
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	7196689	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-15 14:51:53	2020-04-15 14:52:09	1
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	7196715	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-15 14:52:09	2020-04-15 14:52:10	0
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	7196719	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-15 14:52:10	2020-04-15 19:09:26	188
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	7226822	Pendência Sanada - Aprovação	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-15 19:09:26	2020-04-15 19:09:27	0
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	7226823	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-15 19:09:27	2020-04-24 16:04:27	3124
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	7849060	Atendimento Agendado	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 16:04:27	2020-04-24 16:04:27	0
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	7849064	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 16:04:27	2020-04-30 14:43:37	2079
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	8280594	Cancelar	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-30 14:43:37	2020-04-30 14:43:44	0
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	8280618	Encerrar	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-30 14:43:44	2020-04-30 14:43:55	0
            S220048		ATENDER	HR / PY - Carregar informações no SAP através do LSMW	10800	8280639	Cancelado	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-30 14:43:55		0
            T395844	S220048	Execução	HR / PY - Carregar informações no SAP através do LSMW	10800	7226816	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-15 19:09:21	2020-04-15 19:09:21	0
            T395844	S220048	Execução	HR / PY - Carregar informações no SAP através do LSMW	10800	7226817	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-15 19:09:21	2020-04-30 14:43:44	5203
            T395844	S220048	Execução	HR / PY - Carregar informações no SAP através do LSMW	10800	8280617	Encerrar	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-30 14:43:44		0
        """)
            
        self.violated_cancelled_inc_events = Event.parse_events(r"""
            S93146		ATENDER	Outras Solicitações de TIC	540	2775061	Atribuição interna	N	N1-SD2_EMAIL	2020-03-06 01:50:56	2020-03-06 01:50:56	0
            S93146		ATENDER	Outras Solicitações de TIC	540	2775062	Atribuir ao Fornecedor	N	N1-SD2_EMAIL	2020-03-06 01:50:56	2020-03-06 01:57:49	7
            S93146		ATENDER	Outras Solicitações de TIC	540	2775115	Atribuição interna	N	N1-SD2_EMAIL	2020-03-06 01:57:49	2020-03-06 02:14:44	17
            S93146		ATENDER	Outras Solicitações de TIC	540	2775203	Atribuição interna	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-03-06 02:14:44	2020-03-06 02:14:44	0
            S93146		ATENDER	Outras Solicitações de TIC	540	2775205	Atribuir ao Fornecedor	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-03-06 02:14:44	2020-03-06 02:25:01	11
            S93146		ATENDER	Outras Solicitações de TIC	540	2775254	Atribuição interna	N	N2-SD2_SAP_CORP	2020-03-06 02:25:01	2020-03-06 02:25:01	0
            S93146		ATENDER	Outras Solicitações de TIC	540	2775256	Atribuir ao Fornecedor	N	N2-SD2_SAP_CORP	2020-03-06 02:25:01	2020-03-06 07:27:31	27
            S93146		ATENDER	Outras Solicitações de TIC	540	2777777	Atribuição interna	N	N2-SD2_SAP_CORP	2020-03-06 07:27:31	2020-03-06 16:52:03	565
            S93146		ATENDER	Outras Solicitações de TIC	540	2892802	Aguardando Cliente	N	N2-SD2_SAP_CORP	2020-03-06 16:52:03	2020-03-06 16:52:04	0
            S93146		ATENDER	Outras Solicitações de TIC	540	2892804	Aguardando Cliente - Fornecedor	S	N2-SD2_SAP_CORP	2020-03-06 16:52:04	2020-03-06 23:44:11	128
            S93146		ATENDER	Outras Solicitações de TIC	540	2909067	Retorno do usuário	S	N2-SD2_SAP_CORP	2020-03-06 23:44:11	2020-03-06 23:44:12	0
            S93146		ATENDER	Outras Solicitações de TIC	540	2909068	Pendência Sanada	S	N2-SD2_SAP_CORP	2020-03-06 23:44:12	2020-03-06 23:44:13	0
            S93146		ATENDER	Outras Solicitações de TIC	540	2909069	Pendência Sanada - Fornecedor/TIC	N	N2-SD2_SAP_CORP	2020-03-06 23:44:13	2020-03-09 07:35:23	35
            S93146		ATENDER	Outras Solicitações de TIC	540	2962605	Atribuição interna	N	N2-SD2_CONTROLE_DE_DESVIOS	2020-03-09 07:35:23	2020-03-09 07:36:41	1
            S93146		ATENDER	Outras Solicitações de TIC	540	2962673	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-09 07:36:41	2020-03-09 07:36:41	0
            S93146		ATENDER	Outras Solicitações de TIC	540	2962675	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-09 07:36:41	2020-03-09 07:44:00	0
            S93146		ATENDER	Outras Solicitações de TIC	540	2963250	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-09 07:44:00	2020-03-17 11:42:28	3402
            S93146		ATENDER	Outras Solicitações de TIC	540	4047063	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-17 11:42:28	2020-03-17 11:48:33	6
            S93146		ATENDER	Outras Solicitações de TIC	540	4050557	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-17 11:48:33	2020-03-17 17:05:54	317
            S93146		ATENDER	Outras Solicitações de TIC	540	4218075	Retorno do usuário	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-17 17:05:54	2020-03-17 17:45:18	40
            S93146		ATENDER	Outras Solicitações de TIC	540	4234399	Pendência Sanada	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-17 17:45:18	2020-03-17 18:14:56	15
            S93146		ATENDER	Outras Solicitações de TIC	540	4241781	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-17 18:14:56	2020-04-24 14:34:46	13834
            S93146		ATENDER	Outras Solicitações de TIC	540	7834044	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 14:34:46	2020-04-24 14:34:47	0
            S93146		ATENDER	Outras Solicitações de TIC	540	7834050	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 14:34:47	2020-04-28 14:39:11	1085
            S93146		ATENDER	Outras Solicitações de TIC	540	8080291	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-28 14:39:11	2020-04-28 14:39:11	0
            S93146		ATENDER	Outras Solicitações de TIC	540	8080293	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-28 14:39:11	2020-04-28 14:39:58	0
            S93146		ATENDER	Outras Solicitações de TIC	540	8080425	Cancelar	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-28 14:39:58	2020-04-28 14:40:05	0
            S93146		ATENDER	Outras Solicitações de TIC	540	8080441	Encerrar	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-28 14:40:05	2020-04-28 14:40:15	0
            S93146		ATENDER	Outras Solicitações de TIC	540	8080460	Cancelado	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-28 14:40:15		0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2775065	Atribuição interna	N	N1-SD2_EMAIL	2020-03-06 01:51:05	2020-03-06 01:51:05	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2775066	Atribuir ao Fornecedor	N	N1-SD2_EMAIL	2020-03-06 01:51:05	2020-03-06 02:13:27	22
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2775198	Atribuição interna	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-03-06 02:13:27	2020-03-06 02:13:27	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2775200	Atribuir ao Fornecedor	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-03-06 02:13:27	2020-03-06 03:20:55	67
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2775582	Atribuição interna	N	N2-SD2_SAP_CORP	2020-03-06 03:20:55	2020-03-06 03:20:55	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2775584	Atribuir ao Fornecedor	N	N2-SD2_SAP_CORP	2020-03-06 03:20:55	2020-03-06 07:27:55	27
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2777789	Atribuição interna	N	N2-SD2_SAP_CORP	2020-03-06 07:27:55	2020-03-06 17:16:17	589
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2896800	Aguardando Cliente	N	N2-SD2_SAP_CORP	2020-03-06 17:16:17	2020-03-06 17:16:17	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2896801	Aguardando Cliente - Fornecedor	S	N2-SD2_SAP_CORP	2020-03-06 17:16:17	2020-03-09 07:37:24	141
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2962729	Iniciar Atendimento	S	N2-SD2_SAP_CORP	2020-03-09 07:37:24	2020-03-09 07:37:25	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2962730	Pendência Sanada - Fornecedor/TIC	N	N2-SD2_SAP_CORP	2020-03-09 07:37:25	2020-03-09 07:37:39	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2962755	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-09 07:37:39	2020-03-09 07:37:39	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2962757	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-09 07:37:39	2020-03-09 07:43:13	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	2963171	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-09 07:43:13	2020-03-17 11:42:28	3402
            T151841	S93146	Execução	Outras Solicitações de TIC	540	4047065	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-17 11:42:28	2020-03-17 11:48:33	6
            T151841	S93146	Execução	Outras Solicitações de TIC	540	4050552	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-03-17 11:48:33	2020-04-28 14:39:11	15291
            T151841	S93146	Execução	Outras Solicitações de TIC	540	8080292	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-28 14:39:11	2020-04-28 14:39:11	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	8080294	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-28 14:39:11	2020-04-28 14:39:58	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	8080426	Cancelar	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-28 14:39:58	2020-04-28 14:40:05	0
            T151841	S93146	Execução	Outras Solicitações de TIC	540	8080440	Encerrar	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-28 14:40:05		0
        """)
        
        self.prioritized_inc_events = Event.parse_events(r"""
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879757	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:30	2020-05-22 09:53:30	0
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879758	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:30	2020-05-22 09:53:34	0
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879759	Campo do formulário alterado	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:34	2020-05-22 09:53:55	0
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879811	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:55	2020-05-22 09:53:56	0
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879813	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:56	2020-05-22 09:57:08	4
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9880328	Pendência Sanada - Aprovação	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:57:08	2020-05-22 09:57:08	0
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9880330	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:57:08	2020-05-22 10:29:14	32
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9886081	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 10:29:14	2020-05-22 17:29:04	420
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9947854	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 17:29:04	2020-05-22 17:29:04	0
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9947858	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 17:29:04	2020-05-22 18:55:17	86
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9953428	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 18:55:17	2020-05-22 18:55:17	0
            S290168		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9953429	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 18:55:17		6064
            T558229	S290168	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9880314	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:57:01	2020-05-22 09:57:01	0
            T558229	S290168	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9880316	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:57:01	2020-05-22 10:29:43	32
            T558229	S290168	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9886182	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 10:29:43	2020-05-22 17:29:31	420
            T558229	S290168	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9947899	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 17:29:31	2020-05-22 17:29:31	0
            T558229	S290168	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9947901	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 17:29:31	2020-05-22 18:55:12	86
            T558229	S290168	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9953424	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 18:55:12	2020-05-22 18:55:12	0
            T558229	S290168	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9953426	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 18:55:12	2020-05-25 11:31:41	3876
            T558229	S290168	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	10028579	Resolver	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-25 11:31:41		0        
        """)
        
        self.violated_prioritized_inc_events = Event.parse_events(r"""
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879757	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:30	2020-05-22 09:53:30	0
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879758	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:30	2020-05-22 09:53:34	0
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879759	Campo do formulário alterado	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:34	2020-05-22 09:53:55	0
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879811	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:55	2020-05-22 09:53:56	0
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9879813	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:53:56	2020-05-22 09:57:08	4
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9880328	Pendência Sanada - Aprovação	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:57:08	2020-05-22 09:57:08	0
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9880330	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:57:08	2020-05-22 10:29:14	32
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9886081	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 10:29:14	2020-05-22 17:29:04	420
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9947854	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 17:29:04	2020-05-22 17:29:04	0
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9947858	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 17:29:04	2020-05-22 18:55:17	86
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9953428	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 18:55:17	2020-05-22 18:55:17	0
            S290169		ATENDER	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9953429	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 18:55:17		6064
            T558230	S290169	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9880314	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:57:01	2020-05-22 09:57:01	0
            T558230	S290169	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9880316	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 09:57:01	2020-05-22 10:29:43	5400
            T558230	S290169	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9886182	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-22 10:29:43	2020-05-22 17:29:31	420
            T558230	S290169	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9947899	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 17:29:31	2020-05-22 17:29:31	0
            T558230	S290169	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9947901	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 17:29:31	2020-05-22 18:55:12	86
            T558230	S290169	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9953424	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 18:55:12	2020-05-22 18:55:12	0
            T558230	S290169	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	9953426	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 18:55:12	2020-05-25 11:31:41	3876
            T558230	S290169	Execução	MM / Estoques - Criação ou Alteração de DEPÓSITO DE TERCEIROS	2700	10028579	Resolver	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-25 11:31:41		0        
        """)
        
        self.forwarded_inc_events = Event.parse_events("""
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7800809	Atribuição interna	N	N2-SD2_SAP_CORP	2020-04-24 10:35:12	2020-04-24 10:35:12	0
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7800810	Atribuir ao Fornecedor	N	N2-SD2_SAP_CORP	2020-04-24 10:35:12	2020-04-24 10:39:38	4
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7801594	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 10:39:38	2020-04-24 10:39:38	0
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7801597	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 10:39:38	2020-04-24 10:55:43	16
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7804689	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 10:55:43	2020-04-27 09:30:39	455
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7931638	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-27 09:30:39	2020-04-27 09:44:46	14
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7934212	Atribuição interna	N	N4-MAINFRAME-SUSTENTACAO	2020-04-27 09:44:46	2020-04-27 09:44:46	0
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7934215	Atribuir ao Fornecedor	N	N4-MAINFRAME-SUSTENTACAO	2020-04-27 09:44:46	2020-04-27 09:57:16	13
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7936373	Atribuição interna	N	N4-MAINFRAME-SUSTENTACAO	2020-04-27 09:57:16	2020-04-29 10:00:45	1083
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	8139654	Campos alterados	N	N4-MAINFRAME-SUSTENTACAO	2020-04-29 10:00:45	2020-04-29 10:54:34	54
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	8147445	Resolver	N	N4-MAINFRAME-SUSTENTACAO	2020-04-29 10:54:34	2020-05-01 10:58:13	0
            S235312		BD-ALTERACAO-TABELA-SIMPLES	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	8326817	Encerrar	N	N4-MAINFRAME-SUSTENTACAO	2020-05-01 10:58:13		0
            T428435	S235312	Execução	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7800820	Atribuição interna	N	N2-SD2_SAP_CORP	2020-04-24 10:35:20	2020-04-24 10:35:20	0
            T428435	S235312	Execução	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7800821	Atribuir ao Fornecedor	N	N2-SD2_SAP_CORP	2020-04-24 10:35:20	2020-04-24 10:38:25	3
            T428435	S235312	Execução	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7801242	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 10:38:25	2020-04-24 10:38:25	0
            T428435	S235312	Execução	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7801244	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 10:38:25	2020-04-24 10:55:43	17
            T428435	S235312	Execução	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7804694	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-24 10:55:43	2020-04-27 09:40:04	465
            T428435	S235312	Execução	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7933324	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-04-27 09:40:04	2020-04-27 09:43:20	3
            T428435	S235312	Execução	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7933887	Atribuição interna	N	N4-MAINFRAME-SUSTENTACAO	2020-04-27 09:43:20	2020-04-27 09:43:20	0
            T428435	S235312	Execução	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	7933893	Atribuir ao Fornecedor	N	N4-MAINFRAME-SUSTENTACAO	2020-04-27 09:43:20	2020-04-29 10:54:33	1151
            T428435	S235312	Execução	HR / PA - Atualização via INTERFACE para Migração de dados cadastrais entre sistemas que passam pelo SAP ERP (SISPAT/MGBN/GAB/SAM/CVITA-IBM-Gestão/FRE/Busca Aplic Web/SAL/GAIA)	5400	8147437	Resolver	N	N4-MAINFRAME-SUSTENTACAO	2020-04-29 10:54:33		0
        """)
       
        self.violated_forwarded_inc_events = Event.parse_events("""
            S213003		ATENDER	GRC / PC - Outros	5400	6930582	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-04-13 11:09:04	2020-04-13 11:09:04	0
            S213003		ATENDER	GRC / PC - Outros	5400	6930588	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-GRC	2020-04-13 11:09:04	2020-04-13 11:09:07	0
            S213003		ATENDER	GRC / PC - Outros	5400	6930592	Campo do formulário alterado	N	N4-SAP-SUSTENTACAO-GRC	2020-04-13 11:09:07	2020-04-13 11:24:27	15
            S213003		ATENDER	GRC / PC - Outros	5400	6933297	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-04-13 11:24:27	2020-05-13 16:21:34	11097
            S213003		ATENDER	GRC / PC - Outros	5400	9198392	Atribuição interna	N	N4-APOIO_PRODUTO-GRC	2020-05-13 16:21:34	2020-05-13 16:21:34	0
            S213003		ATENDER	GRC / PC - Outros	5400	9198395	Atribuir ao Fornecedor	N	N4-APOIO_PRODUTO-GRC	2020-05-13 16:21:34		17738
            T379624	S213003	Execução	GRC / PC - Outros	5400	6930626	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-04-13 11:09:15	2020-04-13 11:09:15	0
            T379624	S213003	Execução	GRC / PC - Outros	5400	6930627	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-GRC	2020-04-13 11:09:15	2020-04-13 11:24:27	15
            T379624	S213003	Execução	GRC / PC - Outros	5400	6933310	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-04-13 11:24:27	2020-05-19 09:19:22	12835
            T379624	S213003	Execução	GRC / PC - Outros	5400	9572920	Atribuição interna	N	N4-APOIO_PRODUTO-GRC	2020-05-19 09:19:22	2020-05-19 09:19:22	0
            T379624	S213003	Execução	GRC / PC - Outros	5400	9572928	Atribuir ao Fornecedor	N	N4-APOIO_PRODUTO-GRC	2020-05-19 09:19:22		9520        
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
        kpi, observation = self.prs.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente atender processado", observation)
    
    def test_it_computes_the_kpi_for_a_closed_incident(self):
        for evt in self.closed_inc_evts:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_a_closed_incident_that_violated_the_sla(self):
        for evt in self.violated_closed_inc_evts:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
        
    
    def test_it_computes_the_kpi_for_solved_inc_events(self):
        for evt in self.solved_inc_events:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_solved_inc_events_that_violated_the_sla(self):
        for evt in self.violated_solved_inc_events:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
                
    def test_it_computes_the_kpi_for_cancelles_inc_events(self):
        for evt in self.cancelled_inc_events:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
        
    def test_it_computes_the_kpi_for_cancelles_inc_events_that_violated_the_sla(self):
        for evt in self.violated_cancelled_inc_events:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)

    def test_it_compute_the_kpi_for_prioritized_inc_events(self):
        for evt in self.prioritized_inc_events:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
    
    def test_it_compute_the_kpi_for_prioritized_inc_events_that_violated_the_sla_(self):
        for evt in self.violated_prioritized_inc_events:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)

    def test_it_compute_the_kpi_for_forwarded_inc_events(self):
        for evt in self.forwarded_inc_events:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
        
    def test_it_compute_the_kpi_for_forwarded_inc_events_that_violated_the_sla(self):
        for evt in self.violated_forwarded_inc_events:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
        
    def test_it_computes_the_kpi(self):
        for evt in self.events:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(50.0, kpi)
        self.assertEqual("5 violações / 10 incidentes", observation)
        #self.prs.get_details().to_excel("teste.xlsx")
    
    def test_it_skips_incs_with_prior_assignments_and_no_current_assigment(self):
        evts = Event.parse_events(r"""
            TXXXXXX	SYYYYYY	ATENDER	Outras Solicitações de TIC	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-24 23:59:59	0
            TXXXXXX	SYYYYYY	ATENDER	Outras Solicitações de TIC	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
            SYYYYYY		ATENDER	Outras Solicitações de TIC	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-24 23:59:59	0
            SYYYYYY		ATENDER	Outras Solicitações de TIC	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente atender processado", observation)
    
    def test_it_considers_incs_with_prior_assignments_closed_within_period(self):
        evts = Event.parse_events(r"""
            TXXXXXX	SYYYYYY	ATENDER	Outras Solicitações de TIC	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	0
            TXXXXXX	SYYYYYY	ATENDER	Outras Solicitações de TIC	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-26 23:59:59	2020-05-05 14:37:34	0
            SYYYYYY		ATENDER	Outras Solicitações de TIC	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	0
            SYYYYYY		ATENDER	Outras Solicitações de TIC	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-26 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.prs.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prs.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
                