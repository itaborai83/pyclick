import unittest
from pyclick.models import *
from pyclick.n4sap.prc import Prc

class TestPro(unittest.TestCase):
    
    def setUp(self):
        self.click = Click()
        self.prc = Prc()
        self.start_dt = '2020-04-26 00:00:00'
        self.end_dt = '2020-05-26 00:00:00'        
        self.closed_inc_evts = Event.parse_events(r"""
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4293170	Atribuição interna	N	N1-SD2_WEB	2020-03-18 08:35:20	2020-03-18 08:35:20	0
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4293172	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-03-18 08:35:20	2020-03-18 08:35:23	0
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4293174	Campo do formulário alterado	N	N1-SD2_WEB	2020-03-18 08:35:23	2020-03-18 11:07:11	152
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4373779	Atribuição interna	N	N1-SD2_WEB	2020-03-18 11:07:11	2020-03-18 11:19:59	12
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4381092	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-03-18 11:19:59	2020-03-18 11:19:59	0
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4381098	Atribuir ao Fornecedor	N	N2-SD2_SAP_PRAPO	2020-03-18 11:19:59	2020-03-18 11:24:19	5
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4383569	Atribuição interna	N	N2-SD2_SAP_PRAPO	2020-03-18 11:24:19	2020-03-18 11:27:45	3
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4385399	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-18 11:27:45	2020-03-18 11:27:45	0
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4385408	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-18 11:27:45	2020-03-18 11:38:02	11
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4390783	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-18 11:38:02	2020-03-18 11:48:59	10
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	4396745	Pendencia de Fornecedor	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-18 11:48:59	2020-03-24 17:01:11	2473
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	5335307	Retorno do usuário	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-24 17:01:11	2020-03-30 15:36:22	2075
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	5775450	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-30 15:36:22	2020-04-06 17:01:24	2785
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6410628	Pendência de TIC	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-06 17:01:24	2020-04-22 10:39:04	5018
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7637984	Atribuição interna	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-22 10:39:04	2020-04-30 12:18:00	3339
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8263020	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-30 12:18:00	2020-04-30 12:19:34	1
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8263283	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-30 12:19:34	2020-04-30 12:19:35	0
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8263286	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-30 12:19:35	2020-04-30 12:52:03	33
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8267122	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-30 12:52:03	2020-04-30 12:52:04	0
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8267125	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-30 12:52:04	2020-04-30 12:55:25	3
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8267458	Resolver	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-30 12:55:25	2020-05-02 12:57:58	0
            243764		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8347606	Encerrar	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-02 12:57:58		0
        """)

        self.violated_closed_inc_evts = Event.parse_events(r"""
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2377429	Atribuição interna	N	N1-SD2_WEB	2020-03-03 09:30:28	2020-03-03 09:30:28	0
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2377435	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-03-03 09:30:28	2020-03-03 09:30:30	0
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2377439	Campo do formulário alterado	N	N1-SD2_WEB	2020-03-03 09:30:30	2020-03-03 09:31:35	1
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2377676	Atribuição interna	N	N1-SD2_WEB	2020-03-03 09:31:35	2020-03-03 09:37:13	6
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2379076	Atribuição interna	N	N2-SD2_SAP_SERV	2020-03-03 09:37:13	2020-03-03 09:37:13	0
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2379080	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-03-03 09:37:13	2020-03-03 09:50:37	13
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2382419	Atribuição interna	N	N2-SD2_SAP_SERV	2020-03-03 09:50:37	2020-03-03 10:25:12	35
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2391795	Atribuição interna	N	N2-SD2_CONTROLE_DE_DESVIOS	2020-03-03 10:25:12	2020-03-03 10:25:45	0
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2392072	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-03 10:25:45	2020-03-03 10:25:45	0
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2392080	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-03 10:25:45	2020-03-03 10:40:00	15
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	2395671	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-03 10:40:00	2020-03-23 18:14:26	8000
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	5233185	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-23 18:14:26	2020-03-23 18:14:26	0
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	5233187	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-03-23 18:14:26	2020-04-01 15:46:36	3646
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	5999432	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-01 15:46:36	2020-05-13 15:43:25	14577
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9192181	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-13 15:43:25	2020-05-13 15:43:26	0
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9192183	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-13 15:43:26	2020-05-15 18:22:36	1217
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9405616	Resolver	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-05-15 18:22:36	2020-05-15 18:22:36	0
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9405617	Atribuição interna	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-15 18:22:36	2020-05-17 18:22:55	0
            129120		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9448650	Encerrar	S	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-17 18:22:55		0
        """)
        
        self.solved_inc_events = Event.parse_events(r"""
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7731847	Atribuição interna	N	N1-SD2_WEB	2020-04-23 10:43:25	2020-04-23 10:43:25	0
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7731849	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-04-23 10:43:25	2020-04-23 10:45:34	2
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7732159	Atribuição interna	N	N1-SD2_WEB	2020-04-23 10:45:34	2020-04-23 10:51:11	6
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7732872	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-04-23 10:51:11	2020-04-23 10:51:11	0
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7732875	Atribuir ao Fornecedor	N	N2-SD2_SAP_ABGE	2020-04-23 10:51:11	2020-04-23 11:01:44	10
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7733998	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-04-23 11:01:44	2020-04-23 13:31:59	150
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7745383	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-23 13:31:59	2020-04-23 13:31:59	0
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7745385	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-23 13:31:59	2020-04-24 08:37:40	269
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7781478	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 08:37:40	2020-04-24 09:50:00	50
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7792809	Item alterado	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 09:50:00	2020-04-24 12:42:56	172
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7820696	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 12:42:56	2020-04-24 12:42:57	0
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7820698	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 12:42:57	2020-04-24 15:25:55	163
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7842159	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 15:25:55	2020-04-24 15:25:56	0
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7842160	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 15:25:56	2020-04-24 16:05:35	40
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7849242	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 16:05:35	2020-04-30 03:57:41	1735
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8215538	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-30 03:57:41	2020-04-30 12:38:31	218
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8265482	Resolver	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-30 12:38:31	2020-05-02 12:43:03	0
            423514		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8347428	Encerrar	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-05-02 12:43:03		0
        """)
            
        self.violated_solved_inc_events = Event.parse_events(r"""
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7731847	Atribuição interna	N	N1-SD2_WEB	2020-04-23 10:43:25	2020-04-23 10:43:25	0
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7731849	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-04-23 10:43:25	2020-04-23 10:45:34	2
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7732159	Atribuição interna	N	N1-SD2_WEB	2020-04-23 10:45:34	2020-04-23 10:51:11	6
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7732872	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-04-23 10:51:11	2020-04-23 10:51:11	0
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7732875	Atribuir ao Fornecedor	N	N2-SD2_SAP_ABGE	2020-04-23 10:51:11	2020-04-23 11:01:44	10
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7733998	Atribuição interna	N	N2-SD2_SAP_ABGE	2020-04-23 11:01:44	2020-04-23 13:31:59	150
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7745383	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-23 13:31:59	2020-04-23 13:31:59	0
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7745385	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-23 13:31:59	2020-04-24 08:37:40	269
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7781478	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 08:37:40	2020-04-24 09:50:00	50
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7792809	Item alterado	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 09:50:00	2020-04-24 12:42:56	172
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7820696	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 12:42:56	2020-04-24 12:42:57	0
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7820698	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 12:42:57	2020-04-24 15:25:55	163
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7842159	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 15:25:55	2020-04-24 15:25:56	0
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7842160	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 15:25:56	2020-04-24 16:05:35	40
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7849242	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-24 16:05:35	2020-04-30 03:57:41	8735
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8215538	Atribuição interna	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-30 03:57:41	2020-04-30 12:38:31	218
            423515		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8265482	Resolver	N	N4-SAP-SUSTENTACAO-ABAST_GE	2020-04-30 12:38:31		0
        """)

        self.cancelled_inc_events = Event.parse_events(r"""
            447321		CORRIGIR-NÃO EMERGENCIAL			8110233	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-04-28 18:17:35	2020-04-28 18:17:35	0
            447321		CORRIGIR-NÃO EMERGENCIAL			8110234	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-GRC	2020-04-28 18:17:35	2020-04-29 09:08:57	8
            447321		CORRIGIR-NÃO EMERGENCIAL			8130937	Atribuição interna	N	N4-SAP-SUSTENTACAO-GRC	2020-04-29 09:08:57	2020-04-30 17:50:38	1062
            447321		CORRIGIR-NÃO EMERGENCIAL			8310176	Cancelar	N	N4-SAP-SUSTENTACAO-GRC	2020-04-30 17:50:38	2020-04-30 17:50:43	0
            447321		CORRIGIR-NÃO EMERGENCIAL			8310184	Encerrar	N	N4-SAP-SUSTENTACAO-GRC	2020-04-30 17:50:43	2020-04-30 17:50:52	0
            447321		CORRIGIR-NÃO EMERGENCIAL			8310188	Cancelado	N	N4-SAP-SUSTENTACAO-GRC	2020-04-30 17:50:52		0
        """)

        self.violated_cancelled_inc_events = Event.parse_events(r"""
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9201030	Atribuição interna	N	N1-SD2_WEB	2020-05-13 16:40:10	2020-05-13 16:40:10	0
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9201033	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-05-13 16:40:10	2020-05-13 16:40:15	0
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9201036	Campo do formulário alterado	N	N1-SD2_WEB	2020-05-13 16:40:15	2020-05-13 16:44:12	4
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9201480	Atribuição interna	N	N1-SD2_WEB	2020-05-13 16:44:12	2020-05-13 16:51:27	7
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9202499	Item alterado	N	N1-SD2_WEB	2020-05-13 16:51:27	2020-05-13 16:51:51	0
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9202523	Atribuição interna	N	N2-SD2_SAP_CORP	2020-05-13 16:51:51	2020-05-13 16:51:51	0
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9202525	Atribuir ao Fornecedor	N	N2-SD2_SAP_CORP	2020-05-13 16:51:51	2020-05-13 17:01:04	10
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9203616	Atribuição interna	N	N2-SD2_SAP_CORP	2020-05-13 17:01:04	2020-05-13 17:21:11	20
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9205966	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-13 17:21:11	2020-05-13 17:21:11	0
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9205968	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-13 17:21:11	2020-05-13 17:24:27	3
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9206396	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-13 17:24:27	2020-05-14 19:28:06	8576
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9307658	Encerrar	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-14 19:28:06	2020-05-14 19:28:08	0
            516038		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9307659	Cancelar	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-14 19:28:08		0
        """)

        self.prioritized_inc_events = Event.parse_events(r"""
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8779270	Atribuição interna	N	N1-SD2_SAP	2020-05-07 19:17:41	2020-05-07 19:17:41	0
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8779271	Atribuir ao Fornecedor	N	N1-SD2_SAP	2020-05-07 19:17:41	2020-05-07 19:22:46	5
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8779411	Atribuição interna	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-05-07 19:22:46	2020-05-07 19:22:46	0
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8779415	Atribuir ao Fornecedor	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-05-07 19:22:46	2020-05-07 19:25:55	3
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8779489	Atribuição interna	N	N3-CORS_SISTEMAS_SERVICOS_E_APLICACOES_DE_TIC	2020-05-07 19:25:55	2020-05-07 19:47:53	22
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8780137	Atribuição interna	N	N2-SD2_SAP_CORP	2020-05-07 19:47:53	2020-05-07 19:47:53	0
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8780139	Atribuir ao Fornecedor	N	N2-SD2_SAP_CORP	2020-05-07 19:47:53	2020-05-08 07:14:09	14
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8786007	Atribuição interna	N	N2-SD2_SAP_CORP	2020-05-08 07:14:09	2020-05-08 07:19:28	5
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8786174	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-08 07:19:28	2020-05-08 07:19:28	0
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8786176	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-08 07:19:28	2020-05-08 09:13:06	13
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8797053	Atribuição interna	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-08 09:13:06	2020-05-08 09:54:53	41
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8803762	Campos alterados	N	N4-SAP-SUSTENTACAO-CORPORATIVO	2020-05-08 09:54:53	2020-05-08 09:55:21	1
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8803830	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 09:55:21	2020-05-08 09:55:21	0
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8803838	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 09:55:21	2020-05-08 13:10:22	195
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8831930	Campos alterados	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 13:10:22	2020-05-08 13:13:18	3
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8832239	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 13:13:18	2020-05-08 13:13:19	0
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8832242	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 13:13:19	2020-05-08 13:28:57	15
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8833754	Pendência Sanada	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 13:28:57	2020-05-08 13:28:58	0
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8833755	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 13:28:58	2020-05-08 13:30:41	2
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8833937	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-08 13:30:41	2020-05-10 13:33:00	0
            489630		CORRIGIR-PESO35	Dúvida sobre o serviço	99960	8908965	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-10 13:33:00		0
        """)
        
        self.violated_prioritized_inc_events = Event.parse_events(r"""
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9690944	Atribuição interna	N	N1-SD2_WEB	2020-05-20 11:11:09	2020-05-20 11:11:09	0
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9690946	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-05-20 11:11:09	2020-05-20 11:13:42	2
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9691333	Atribuição interna	N	N1-SD2_WEB	2020-05-20 11:13:42	2020-05-20 11:18:17	5
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9692278	Item alterado	N	N1-SD2_WEB	2020-05-20 11:18:17	2020-05-20 11:19:23	1
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9692482	Atribuição interna	N	N2-SD2_SAP_FIN	2020-05-20 11:19:23	2020-05-20 11:19:23	0
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9692493	Atribuir ao Fornecedor	N	N2-SD2_SAP_FIN	2020-05-20 11:19:23	2020-05-20 11:38:08	19
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9696142	Atribuição interna	N	N2-SD2_SAP_FIN	2020-05-20 11:38:08	2020-05-20 11:50:00	12
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9698353	Aguardando Cliente	N	N2-SD2_SAP_FIN	2020-05-20 11:50:00	2020-05-20 11:50:01	0
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9698356	Aguardando Cliente - Fornecedor	S	N2-SD2_SAP_FIN	2020-05-20 11:50:01	2020-05-20 13:14:42	84
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9709745	Iniciar Atendimento	S	N2-SD2_SAP_FIN	2020-05-20 13:14:42	2020-05-20 13:14:43	0
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9709746	Pendência Sanada - Fornecedor/TIC	N	N2-SD2_SAP_FIN	2020-05-20 13:14:43	2020-05-20 13:15:25	1
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9709809	Atribuição interna	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-20 13:15:25	2020-05-20 13:15:25	0
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9709814	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-20 13:15:25	2020-05-20 13:34:55	19
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9711930	Atribuição interna	N	N4-SAP-SUSTENTACAO-FINANCAS	2020-05-20 13:34:55	2020-05-20 15:06:54	9200
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9724788	Atribuição interna	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-20 15:06:54	2020-05-20 15:06:54	0
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9724791	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-20 15:06:54	2020-05-20 15:31:57	25
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9728827	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-20 15:31:57	2020-05-20 15:31:57	0
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9728829	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-20 15:31:57	2020-05-22 11:33:32	2642
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9897661	Iniciar Atendimento	S	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 11:33:32	2020-05-22 11:33:33	0
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9897663	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 11:33:33	2020-05-22 11:42:25	9
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9899128	Resolver	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-22 11:42:25	2020-05-24 11:42:56	0
            545658		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9982914	Encerrar	N	N4-SAP-SUSTENTACAO-PRIORIDADE	2020-05-24 11:42:56		0            
        """)
            
        self.forwarded_inc_events = Event.parse_events("""
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6354684	Atribuição interna	N	N1-SD2_WEB	2020-04-06 10:43:34	2020-04-06 10:43:34	0
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6354686	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-04-06 10:43:34	2020-04-06 10:43:37	0
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6354688	Campo do formulário alterado	N	N1-SD2_WEB	2020-04-06 10:43:37	2020-04-06 10:47:44	4
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6355417	Atribuição interna	N	N1-SD2_WEB	2020-04-06 10:47:44	2020-04-06 10:50:24	3
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6355945	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-06 10:50:24	2020-04-06 10:50:24	0
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6355949	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-04-06 10:50:24	2020-04-06 10:57:38	7
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6357099	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-06 10:57:38	2020-04-06 10:58:38	1
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6357254	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-06 10:58:38	2020-04-06 10:58:38	0
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6357259	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-06 10:58:38	2020-04-06 12:10:07	72
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6369685	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-06 12:10:07	2020-04-06 12:11:00	1
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6369830	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-06 12:11:00	2020-04-06 14:54:42	163
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6390948	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-06 14:54:42	2020-04-09 10:13:54	1339
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6696152	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 10:13:54	2020-04-09 10:13:55	0
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6696155	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 10:13:55	2020-05-13 15:12:29	11639
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9186378	Atribuição interna	S	N4-SAP-DEMANDAS-SBS	2020-05-13 15:12:29	2020-05-13 15:12:29	0
            351011		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	9186385	Atribuir ao Fornecedor	S	N4-SAP-DEMANDAS-SBS	2020-05-13 15:12:29		4488
        
        """)
        
        self.violated_forwarded_inc_events = Event.parse_events("""
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6362194	Atribuição interna	N	N1-SD2_WEB	2020-04-06 11:26:05	2020-04-06 11:26:05	0
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6362195	Atribuir ao Fornecedor	N	N1-SD2_WEB	2020-04-06 11:26:05	2020-04-06 11:26:09	0
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6362197	Campo do formulário alterado	N	N1-SD2_WEB	2020-04-06 11:26:09	2020-04-06 11:31:33	5
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6362953	Atribuição interna	N	N1-SD2_WEB	2020-04-06 11:31:33	2020-04-06 11:36:08	5
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6363786	Atribuição interna	N	N2-SD2_SAP_SERV	2020-04-06 11:36:08	2020-04-06 11:36:08	0
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6363789	Atribuir ao Fornecedor	N	N2-SD2_SAP_SERV	2020-04-06 11:36:08	2020-04-06 11:37:06	1
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6363902	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-06 11:37:06	2020-04-06 11:37:06	0
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6363906	Atribuir ao Fornecedor	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-06 11:37:06	2020-04-06 12:13:10	36
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6370166	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-06 12:13:10	2020-04-07 11:47:51	514
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6481473	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-07 11:47:51	2020-04-09 10:14:21	987
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6696244	Aguardando Cliente	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 10:14:21	2020-04-09 10:14:22	0
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	6696250	Aguardando Cliente - Fornecedor	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-09 10:14:22	2020-04-16 14:40:32	2426
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7305701	Pendência Sanada	S	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-16 14:40:32	2020-04-16 14:40:32	0
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	7305703	Pendência Sanada - Fornecedor/TIC	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-16 14:40:32	2020-04-30 08:45:31	9520
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8223725	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-30 08:45:31	2020-04-30 21:24:33	540
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8317804	Atribuição interna	N	N4-SAP-DEMANDAS-SBS	2020-04-30 21:24:33	2020-04-30 21:24:33	0
            351487		CORRIGIR-NÃO EMERGENCIAL	Suporte ao serviço de SAP	540	8317806	Atribuir ao Fornecedor	N	N4-SAP-DEMANDAS-SBS	2020-04-30 21:24:33		8640
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
        kpi, observation = self.prc.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente corrigir processado", observation)

    def test_it_computes_the_kpi_for_a_closed_incident(self):
        for evt in self.closed_inc_evts:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
        
    def test_it_computes_the_kpi_for_a_closed_incident_that_violated_the_sla(self):
        for evt in self.violated_closed_inc_evts:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
        
    def test_it_computes_the_kpi_for_solved_inc_events(self):
        for evt in self.solved_inc_events:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)

    def test_it_computes_the_kpi_for_solved_inc_events_that_violated_the_sla(self):
        for evt in self.violated_solved_inc_events:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
        
    def test_it_computes_the_kpi_for_cancelles_inc_events(self):
        for evt in self.cancelled_inc_events:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
    

    def test_it_computes_the_kpi_for_cancelles_inc_events_that_violated_the_sla(self):
        for evt in self.violated_cancelled_inc_events:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)


    def test_it_compute_the_kpi_for_prioritized_inc_events(self):
        for evt in self.prioritized_inc_events:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
        
    def test_it_compute_the_kpi_for_prioritized_inc_events_that_violated_the_sla(self):
        for evt in self.violated_prioritized_inc_events:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
    
    def test_it_compute_the_kpi_for_forwarded_inc_events(self):
        for evt in self.forwarded_inc_events:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)
        
    def test_it_compute_the_kpi_for_forwarded_inc_events_that_violated_the_sla(self):
        for evt in self.violated_forwarded_inc_events:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(100.0, kpi)
        self.assertEqual("1 violações / 1 incidentes", observation)
        
    def test_it_computes_the_kpi(self):
        for evt in self.events:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(50.0, kpi)
        self.assertEqual("5 violações / 10 incidentes", observation)
        #self.prc.get_details().to_excel("teste.xlsx")

    def test_it_skips_incs_with_prior_assignments_and_no_current_assigment(self):
        evts = Event.parse_events(r"""
            XXXXXX		CORRIGIR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-24 23:59:59	0        
            XXXXXX		CORRIGIR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-24 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(None, kpi)
        self.assertEqual("Nenhum incidente corrigir processado", observation)

    def test_it_considers_incs_with_prior_assignments_closed_within_period(self):
        evts = Event.parse_events(r"""
            XXXXXX		CORRIGIR	Dúvida sobre o serviço	99960	8193373	Atribuição interna	N	N4-SAP-SUSTENTACAO-SERVICOS	2020-04-24 00:00:00	2020-04-26 23:59:59	0
            XXXXXX		CORRIGIR	Dúvida sobre o serviço	99960	8541250	Atribuição interna	S	N6-SAP-XXXXXXXXXXXXXXXXXXXXXX	2020-04-26 23:59:59	2020-05-05 14:37:34	0
        """)
        for evt in evts:
            self.click.update(evt)
        self.prc.evaluate(self.click, self.start_dt, self.end_dt)
        kpi, observation = self.prc.get_result()
        self.assertEqual(0.0, kpi)
        self.assertEqual("0 violações / 1 incidentes", observation)