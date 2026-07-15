"""
Mensagens de exemplo simulando e-mail/comunicados recebidos por uma
trading de algodão sobre reclamações de qualidade, disputas de embarque
e outras correspondências comuns.

Este módulo não depende de nenhum outro arquivo de projeto; é dado puro,
usado por chains, grafos e testes manuais no REPL.
"""

CLAIMS = [
    # Claim 0: contaminação, alta exposição financeira -> deve escalar
    """
    Date: June 3, 2026
    From: Meridian Textile Mills, Contract MTM-2026-0417
    To: Cerrado Cotton Trading Co.
    Shipment: Lot BR-CT-88231, Origin Cuiabá, Mato Grosso, Brazil

    During opening of bales from the above shipment, our incoming
    inspection team identified significant plastic contamination
    across multiple bales (approximately 6% of the lot by weight).
    This is a serious breach of the ICA Bylaws contamination
    tolerance clause under our contract.

    Additionally, HVI results on a 20-bale sample show micronaire
    averaging 3.2, below the contracted 3.7-4.2 range, and staple
    length averaging 33 (1 3/32"), below the contracted 35 (1 3/32"+).

    Required Actions:
    We require immediate confirmation of claim acceptance, a full
    re-classification of the lot by an independent Bremen/ICA-approved
    classer, and a proposal for price adjustment or replacement.

    Deadline for Response: We require a response within 5 business
    days of this notice. Failure to respond may result in formal
    ICA arbitration proceedings and a claim for damages up to
    USD 180,000.

    Contact: For questions, contact our quality department at
    +1 (704) 555-0182 or claims@meridiantextile.com.
    """,
    # Claim 1: fatura, não é reclamação -> deve ser roteada pro financeiro
    """
    From: billing@ginlogistics.com.br

    Prezados,

    Segue em anexo a fatura referente ao frete de 480 fardos do lote
    BR-CT-88104, no valor de R$ 62.400,00, com vencimento em 20 dias.

    Qualquer dúvida, estamos à disposição.

    Atenciosamente,
    Gin Logistics Transportes
    """,
    # Claim 2: reclamação de cliente, linguagem informal, sem termos técnicos
    # explícitos de contrato -> testa se o agente reconhece como reclamação
    """
    From: procurement@anatoliayarns.com.tr

    Hi team,

    We've had some trouble with the last two container loads from you.
    The quality just isn't matching what we usually get from Brazilian
    origin — a lot more short fiber and neps than expected, and our
    spinning line has been having more breaks than usual. Can someone
    look into this and let us know what you can do?

    Thanks,
    Deniz
    """,
    # Claim 3: disputa de peso com um gin doméstico, baixa exposição,
    # sem contaminação -> não deve escalar, mas pode gerar follow-up
    """
    Data: 14 de julho de 2026
    De: Algodoeira Vale do Cerrado
    Para: Cerrado Cotton Trading Co.
    Referente: Lote BR-CT-88350, Fazenda Santa Rita, Primavera do Leste, MT

    Prezados,

    Na conferência de peso na chegada ao armazém, identificamos uma
    diferença de 340 kg a menos em relação ao romaneio original de
    embarque (18.200 kg previstos contra 17.860 kg recebidos).

    Não há indícios de contaminação ou problema de classificação HVI.
    Solicitamos revisão do romaneio e, se confirmada a divergência,
    ajuste no valor da nota.

    Prazo para resposta: 10 dias úteis.

    Atenciosamente,
    Setor de Recebimento
    """,
]
