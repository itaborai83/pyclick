import unittest
from pyclick.models import *
from pyclick.n4sap.models import *
from pyclick.n4sap.prp import PrpV2

class TestPrp(unittest.TestCase):
    
    def setUp(self):
        self.incsrv = IncidentService()
        self.click = ClickN4(self.incsrv)
        self.prp = PrpV2(self.incsrv)
        self.start_dt = '2020-04-26 00:00:00'
        self.end_dt = '2020-05-26 00:00:00'
        self.closed_inc_evts = Event.parse_events(r"""
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7322803	Atribuição interna	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:09:32	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7322804	Atribuir ao Fornecedor	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:20:18	11
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7324671	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:20:18	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7324673	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:23:08	3
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7325015	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:23:08	2020-04-17 11:02:00	219
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7380505	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 11:02:00	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7380508	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 17:59:49	417
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7437217	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:49	2020-04-17 17:59:50	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	7437218	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:50	2020-05-04 21:31:00	24692
            400982		ORIENTAR	Dúvida sobre o serviço	99960	8474333	Resolver	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 21:31:00	2020-05-06 21:32:56	0
            400982		ORIENTAR	Dúvida sobre o serviço	99960	8678175	Encerrar	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 21:32:56		0        
        """)

        self.violated_closed_inc_evts = Event.parse_events(r"""
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7322803	Atribuição interna	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:09:32	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7322804	Atribuir ao Fornecedor	N	N1-SD2_SAP	2020-04-16 16:09:32	2020-04-16 16:20:18	11
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7324671	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:20:18	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7324673	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:20:18	2020-04-16 16:23:08	3
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7325015	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-16 16:23:08	2020-04-17 11:02:00	219
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7380505	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 11:02:00	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7380508	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 11:02:00	2020-04-17 17:59:49	417
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7437217	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:49	2020-04-17 17:59:50	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	7437218	Aguardando Cliente - Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-17 17:59:50	2020-05-04 21:31:00	24692
            400983		ORIENTAR	Dúvida sobre o serviço	99960	8474333	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 21:31:00	2020-05-06 21:32:56	0
            400983		ORIENTAR	Dúvida sobre o serviço	99960	8678175	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 21:32:56		0        
        """)
        
        self.solved_inc_events = Event.parse_events(r"""
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032069	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:52	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032070	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:57	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032071	Campo do formulário alterado	N	N1-SD2_WEB	2020-02-27 15:14:57	2020-02-27 15:23:33	9
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2034015	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:23:33	2020-02-27 15:44:14	21
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038309	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:44:14	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038315	Atribuir ao Fornecedor	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:56:56	12
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041363	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:56:56	2020-02-27 15:59:16	3
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041836	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 15:59:16	2020-02-27 15:59:16	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041841	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 15:59:16	2020-02-27 16:00:59	1
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2042290	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 16:00:59	2020-02-28 17:33:57	633
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158921	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-28 17:33:57	2020-02-28 17:34:16	1
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158951	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-28 17:34:16	2020-03-02 14:58:48	384
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2317548	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-02 14:58:48	2020-03-03 17:55:48	717
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2479011	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-03 17:55:48	2020-03-05 17:37:11	1062
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764051	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-05 17:37:11	2020-03-05 17:39:11	2
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764262	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-05 17:39:11	2020-04-06 10:15:47	11436
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6349995	Pendência de TIC	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-06 10:15:47	2020-04-20 10:34:54	4879
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7519497	Aguardando Cliente	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-20 10:34:54	2020-04-27 15:25:06	2451
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988865	Retorno do usuário	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:06	2020-04-27 15:25:07	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988866	Pendência Sanada	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:07	2020-04-27 15:25:09	0
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988868	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:09	2020-04-27 15:26:34	1
            110322		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7989088	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:26:34		0
        """)

        self.violated_solved_inc_events = Event.parse_events(r"""
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032069	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:52	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032070	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-02-27 15:14:52	2020-02-27 15:14:57	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2032071	Campo do formulário alterado	N	N1-SD2_WEB	2020-02-27 15:14:57	2020-02-27 15:23:33	9
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2034015	Atribuição interna	N	N1-SD2_WEB	2020-02-27 15:23:33	2020-02-27 15:44:14	21
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038309	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:44:14	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2038315	Atribuir ao Fornecedor	N	N2-SD2_SAP_PRAPO	2020-02-27 15:44:14	2020-02-27 15:56:56	12
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041363	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-02-27 15:56:56	2020-02-27 15:59:16	3
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041836	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 15:59:16	2020-02-27 15:59:16	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2041841	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 15:59:16	2020-02-27 16:00:59	1
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2042290	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-27 16:00:59	2020-02-28 17:33:57	633
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158921	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-28 17:33:57	2020-02-28 17:34:16	1
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2158951	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-02-28 17:34:16	2020-03-02 14:58:48	384
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2317548	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-02 14:58:48	2020-03-03 17:55:48	717
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2479011	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-03 17:55:48	2020-03-05 17:37:11	1062
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764051	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-05 17:37:11	2020-03-05 17:39:11	2
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2764262	Campos alterados	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-03-05 17:39:11	2020-04-06 10:15:47	11436
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6349995	Pendência de TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-06 10:15:47	2020-04-20 10:34:54	4879
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7519497	Aguardando Cliente	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-20 10:34:54	2020-04-27 15:25:06	2451
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988865	Retorno do usuário	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:06	2020-04-27 15:25:07	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988866	Pendência Sanada	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:07	2020-04-27 15:25:09	0
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7988868	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:25:09	2020-04-27 15:26:34	1
            110323		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7989088	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-27 15:26:34		0
        """)
        
        self.cancelled_inc_events = Event.parse_events(r"""
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772322	Atribuição interna	N	N1-SD2_WEB	2020-05-07 17:28:56	2020-05-07 17:28:56	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772324	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-05-07 17:28:56	2020-05-07 17:28:58	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772326	Campo do formulário alterado	N	N1-SD2_WEB	2020-05-07 17:28:58	2020-05-07 17:31:40	3
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772654	Atribuição interna	N	N1-SD2_WEB	2020-05-07 17:31:40	2020-05-07 17:32:57	1
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772797	Item alterado	N	N1-SD2_WEB	2020-05-07 17:32:57	2020-05-07 17:33:26	1
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772854	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-05-07 17:33:26	2020-05-07 17:33:26	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772858	Atribuir ao Fornecedor	N	N2-SD2_SAP_ABGE	2020-05-07 17:33:26	2020-05-07 17:36:24	3
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8773196	Atribuição interna	N	N2-SD2_SAP_SERV	2020-05-07 17:36:24	2020-05-07 18:05:48	29
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8775700	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:05:48	2020-05-07 18:05:48	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8775702	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:05:48	2020-05-07 18:31:18	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8777229	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:31:18	2020-05-07 19:22:25	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779407	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:22:25	2020-05-07 19:22:25	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779409	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:22:25	2020-05-07 19:29:48	7
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779634	Cancelar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:29:48	2020-05-07 19:29:54	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779635	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:29:54	2020-05-07 19:30:04	0
            489119		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779640	Cancelado	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:30:04		0        
        """)
        
        self.violated_cancelled_inc_events = Event.parse_events(r"""
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772322	Atribuição interna	N	N1-SD2_WEB	2020-05-07 17:28:56	2020-05-07 17:28:56	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772324	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-05-07 17:28:56	2020-05-07 17:28:58	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772326	Campo do formulário alterado	N	N1-SD2_WEB	2020-05-07 17:28:58	2020-05-07 17:31:40	3
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772654	Atribuição interna	N	N1-SD2_WEB	2020-05-07 17:31:40	2020-05-07 17:32:57	1
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772797	Item alterado	N	N1-SD2_WEB	2020-05-07 17:32:57	2020-05-07 17:33:26	1
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772854	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-05-07 17:33:26	2020-05-07 17:33:26	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8772858	Atribuir ao Fornecedor	N	N2-SD2_SAP_ABGE	2020-05-07 17:33:26	2020-05-07 17:36:24	3
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8773196	Atribuição interna	N	N2-SD2_SAP_SERV	2020-05-07 17:36:24	2020-05-07 18:05:48	29
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8775700	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:05:48	2020-05-07 18:05:48	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8775702	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:05:48	2020-05-07 18:31:18	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8777229	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-07 18:31:18	2020-05-07 19:22:25	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779407	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:22:25	2020-05-07 19:22:25	540
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779409	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:22:25	2020-05-07 19:29:48	7
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779634	Cancelar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:29:48	2020-05-07 19:29:54	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779635	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:29:54	2020-05-07 19:30:04	0
            489120		ABAST - Faturamento - Impacto Fiscal	Suporte aos serviços críticos	540	8779640	Cancelado	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-07 19:30:04		0        
        """)
        
        self.deprioritized_inc_events = Event.parse_events(r"""
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7643434	Atribuição interna	N	N1-SD2_CHAT_HUMANO	2020-04-22 11:05:40	2020-04-22 11:05:40	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7643435	Atribuir ao Fornecedor	N	N1-SD2_CHAT_HUMANO	2020-04-22 11:05:40	2020-04-22 11:26:45	21
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7647806	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-22 11:26:45	2020-04-22 11:26:45	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7647808	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-04-22 11:26:45	2020-04-22 11:28:14	2
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7648053	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-22 11:28:14	2020-04-22 14:28:37	180
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7672162	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:28:37	2020-04-22 14:28:37	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7672167	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:28:37	2020-04-22 14:40:19	12
            418348		ORIENTAR	Dúvida sobre o serviço	99960	7674402	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:40:19	2020-04-27 17:58:46	1818
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8010478	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-27 17:58:46	2020-04-29 16:06:57	968
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:06:57	2020-04-29 16:06:57	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8193377	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:06:57	2020-04-29 16:07:40	1
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8193482	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:07:40	2020-04-29 16:07:41	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8193485	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:07:41	2020-05-05 14:37:34	8550
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 14:37:34	2020-05-05 14:37:34	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8541252	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 14:37:34	2020-05-11 15:41:10	2224
            418348		ORIENTAR	Dúvida sobre o serviço	99960	8991593	Resolver	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-11 15:41:10	2020-05-13 15:43:01	0
            418348		ORIENTAR	Dúvida sobre o serviço	99960	9192079	Encerrar	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-13 15:43:01		0        
        """)
        
        self.violated_deprioritized_inc_events = Event.parse_events(r"""
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7643434	Atribuição interna	N	N1-SD2_CHAT_HUMANO	2020-04-22 11:05:40	2020-04-22 11:05:40	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7643435	Atribuir ao Fornecedor	N	N1-SD2_CHAT_HUMANO	2020-04-22 11:05:40	2020-04-22 11:26:45	21
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7647806	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-22 11:26:45	2020-04-22 11:26:45	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7647808	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-04-22 11:26:45	2020-04-22 11:28:14	2
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7648053	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-22 11:28:14	2020-04-22 14:28:37	180
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7672162	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:28:37	2020-04-22 14:28:37	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7672167	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:28:37	2020-04-22 14:40:19	12
            418349		ORIENTAR	Dúvida sobre o serviço	99960	7674402	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 14:40:19	2020-04-27 17:58:46	1818
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8010478	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-27 17:58:46	2020-04-29 16:06:57	968
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:06:57	2020-04-29 16:06:57	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8193377	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:06:57	2020-04-29 16:07:40	1
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8193482	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:07:40	2020-04-29 16:07:41	540
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8193485	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-29 16:07:41	2020-05-05 14:37:34	8550
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 14:37:34	2020-05-05 14:37:34	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8541252	Atribuir ao Fornecedor	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 14:37:34	2020-05-11 15:41:10	2224
            418349		ORIENTAR	Dúvida sobre o serviço	99960	8991593	Resolver	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-11 15:41:10	2020-05-13 15:43:01	0
            418349		ORIENTAR	Dúvida sobre o serviço	99960	9192079	Encerrar	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-13 15:43:01		0        
        """)
        
        self.service_request_and_task_inc_events = Event.parse_events(r"""
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411672	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:17:56	2020-05-04 11:17:56	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411674	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:17:56	2020-05-04 11:18:14	1
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411714	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:14	2020-05-04 11:18:14	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411718	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:14	2020-05-04 11:18:29	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411772	Pendência Sanada - Aprovação	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:29	2020-05-04 11:18:30	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411774	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:30	2020-05-04 11:20:38	2
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412271	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:20:38	2020-05-05 16:12:48	832
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557671	Atendimento Agendado	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-05 16:12:48	2020-05-05 16:12:49	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557672	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-05 16:12:49	2020-05-06 09:47:26	155
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597552	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:47:26	2020-05-06 09:47:27	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597555	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:47:27	2020-05-06 09:55:14	8
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598963	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:55:14	2020-05-08 09:58:04	0
            S251253		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8804245	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 09:58:04		0
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411754	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:24	2020-05-04 11:18:24	0
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411756	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:24	2020-05-04 11:21:30	3
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412440	Atribuição interna	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:21:30	2020-05-06 09:55:13	994
            T465903	S251253	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598958	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:55:13		0        
        """)

        self.violated_service_request_and_task_inc_events = Event.parse_events(r"""
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411672	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:17:56	2020-05-04 11:17:56	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411674	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:17:56	2020-05-04 11:18:14	1
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411714	Aguardando Cliente - Aprovação	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:14	2020-05-04 11:18:14	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411718	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:14	2020-05-04 11:18:29	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411772	Pendência Sanada - Aprovação	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:29	2020-05-04 11:18:30	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411774	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:30	2020-05-04 11:20:38	2
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412271	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:20:38	2020-05-05 16:12:48	832
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557671	Atendimento Agendado	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-05 16:12:48	2020-05-05 16:12:49	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8557672	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-05 16:12:49	2020-05-06 09:47:26	155
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597552	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:47:26	2020-05-06 09:47:27	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8597555	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:47:27	2020-05-06 09:55:14	8
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598963	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:55:14	2020-05-08 09:58:04	0
            S251254		ATENDER	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8804245	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 09:58:04		0
            T465904	S251254	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411754	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:24	2020-05-04 11:18:24	0
            T465904	S251254	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8411756	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:18:24	2020-05-04 11:21:30	3
            T465904	S251254	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8412440	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-04 11:21:30	2020-05-06 09:55:13	994
            T465904	S251254	Execução	FI-AA - Alteração de atribuicao contas do razão imobilizado	5400	8598958	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-06 09:55:13		0        
        """)
        
        self.incident_S207728_evts = Event.parse_events(r"""
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6716525	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 12:04:38	2020-04-09 12:04:38	0
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6716527	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 12:04:38	2020-04-09 12:04:42	0
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6716529	Campo do formulário alterado	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 12:04:42	2020-04-09 12:08:37	4
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6717085	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 12:08:37	2020-04-09 14:17:51	129
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6732195	Campos alterados	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 14:17:51	2020-04-09 14:19:05	2
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6732379	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-09 14:19:05	2020-04-09 14:19:05	0
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6732381	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-09 14:19:05	2020-04-09 19:15:47	296
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6772568	Atribuição interna	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-09 19:15:47	2020-04-09 19:15:47	0
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6772571	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-09 19:15:47	2020-04-13 08:54:14	0
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6904291	Campos alterados	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-13 08:54:14	2020-04-13 17:40:54	520
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	6997073	Atribuição interna	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-13 17:40:54	2020-04-17 15:31:18	2031
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	7418033	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-17 15:31:18	2020-04-17 15:31:18	0
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	7418035	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-17 15:31:18	2020-05-05 13:37:01	5286
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	8533124	Pendência Sanada	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 13:37:01	2020-05-05 13:37:01	0
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	8533125	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-05 13:37:01	2020-05-22 15:40:53	7143
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	9932947	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-22 15:40:53	2020-05-22 15:40:54	0
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	9932950	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-22 15:40:54	2020-05-25 18:39:57	680
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	10083353	Pendência Sanada	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-25 18:39:57	2020-05-25 18:39:58	0
            S207728		ATENDER-PESO30-120H	MM - Outros	2700	10083354	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-25 18:39:58		540
            T369882	S207728	Execução	MM - Outros	2700	6716567	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 12:04:48	2020-04-09 12:04:48	0
            T369882	S207728	Execução	MM - Outros	2700	6716569	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 12:04:48	2020-04-09 12:08:37	4
            T369882	S207728	Execução	MM - Outros	2700	6717096	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 12:08:37	2020-04-09 14:19:05	131
            T369882	S207728	Execução	MM - Outros	2700	6732385	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-09 14:19:05	2020-04-09 14:19:05	0
            T369882	S207728	Execução	MM - Outros	2700	6732389	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-09 14:19:05	2020-04-14 10:32:51	6973
            T369882	S207728	Execução	MM - Outros	2700	7050175	Atribuição interna	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-14 10:32:51	2020-04-14 10:32:51	0
            T369882	S207728	Execução	MM - Outros	2700	7050178	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-04-14 10:32:51	2020-05-22 15:40:46	14348
            T369882	S207728	Execução	MM - Outros	2700	9932925	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-22 15:40:46	2020-05-22 15:40:47	0
            T369882	S207728	Execução	MM - Outros	2700	9932930	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-22 15:40:47	2020-05-25 18:39:50	680
            T369882	S207728	Execução	MM - Outros	2700	10083344	Pendência Sanada	S	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-25 18:39:50	2020-05-25 18:39:52	0
            T369882	S207728	Execução	MM - Outros	2700	10083347	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-25 18:39:52	2020-05-25 18:42:10	0
            T369882	S207728	Execução	MM - Outros	2700	10083463	Resolver	N	N4-SAP-SUSTENTACAO-ESCALADOS	2020-05-25 18:42:10	2020-05-25 18:42:10	0
            T369882	S207728	Execução	MM - Outros	2700	10083467	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-25 18:42:10		540
        """)
        

        self.events = self.closed_inc_evts                                \
        +             self.violated_closed_inc_evts                       \
        +             self.solved_inc_events                              \
        +             self.violated_solved_inc_events                     \
        +             self.cancelled_inc_events                           \
        +             self.violated_cancelled_inc_events                  \
        +             self.deprioritized_inc_events                       \
        +             self.violated_deprioritized_inc_events              \
        +             self.service_request_and_task_inc_events            \
        +             self.violated_service_request_and_task_inc_events        
        
    def tearDown(self):
        pass
    
    def test_it_computes_the_kpi_for_no_incidents(self):
        kpi, observation = self.prp.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente peso 35 processado", observation)

    def test_it_computes_the_kpi_for_a_closed_incident(self):
        for evt in self.closed_inc_evts:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)

    def test_it_computes_the_kpi_for_a_closed_incident_that_violated_the_sla(self):
        for evt in self.violated_closed_inc_evts:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_solved_inc_events(self):
        for evt in self.solved_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
        
    def test_it_computes_the_kpi_for_solved_inc_events_that_violated_the_sla(self):
        for evt in self.violated_solved_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_cancelles_inc_events(self):
        for evt in self.cancelled_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_cancelles_inc_events_that_violated_the_sla(self):
        for evt in self.violated_cancelled_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_compute_the_kpi_for_deprioritized_inc_events(self):
        for evt in self.deprioritized_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)    
    
    def test_it_compute_the_kpi_for_deprioritized_inc_events_that_violated_the_sla(self):
        for evt in self.violated_deprioritized_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_service_requests_and_their_tasks(self):
        for evt in self.service_request_and_task_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
    
    def test_it_computes_the_kpi_for_service_requests_and_their_tasks_that_violated_the_sla(self):
        for evt in self.violated_service_request_and_task_inc_events:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)

    def test_it_does_not_consider_assignments_prior_the_period(self):
        for evt in self.incident_S207728_evts:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente peso 35 processado", observation)

    def test_it_computes_the_kpi(self):
        for evt in self.events:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(50.0, kpi)
        self.assertEqual("5 violações / 10 incidentes", observation)
        #self.prp.get_details().to_excel("teste.xlsx")
    
    def test_it_skips_incs_with_prior_assignments_and_no_current_assigment(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-24 00:00:00	2020-04-24 23:59:59	0        
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente peso 35 processado", observation)

    def test_it_considers_incs_with_prior_assignments_closed_within_period(self):
        evts = Event.parse_events(r"""
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-04-24 00:00:00	2020-04-26 23:59:59	0
            XXXXXX		ORIENTAR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-26 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.prp.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prp.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente peso 35 processado", observation)
        