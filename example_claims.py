"""
Sample messages simulating emails/notices received by a cotton trading
company about quality claims, shipment disputes, and other common
correspondence.

This module does not depend on any other project file; it is pure data,
used by chains, graphs, and manual tests in the REPL.
"""

CLAIMS = [
    # Claim 0: contamination, high financial exposure -> should escalate
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
    # Claim 1: invoice, not a claim -> should be routed to finance
    """
    From: billing@ginlogistics.com.br

    Dear Sir/Madam,

    Please find attached the invoice for freight on 480 bales from lot
    BR-CT-88104, in the amount of R$ 62,400.00, due in 20 days.

    Please let us know if you have any questions.

    Best regards,
    Gin Logistics Transportes
    """,
    # Claim 2: customer complaint, informal language, no explicit contract
    # technical terms -> tests whether the agent recognizes it as a claim
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
    # Claim 3: weight dispute with a domestic gin, low exposure, no
    # contamination -> should not escalate, but may generate follow-up
    """
    Date: July 14, 2026
    From: Cerrado Valley Ginnery
    To: Cerrado Cotton Trading Co.
    Reference: Lot BR-CT-88350, Santa Rita Farm, Primavera do Leste, MT

    Dear Sir/Madam,

    During the weight check upon arrival at the warehouse, we identified
    a shortfall of 340 kg compared to the original shipping packing list
    (18,200 kg expected versus 17,860 kg received).

    There are no signs of contamination or HVI classification issues.
    We request a review of the packing list and, if the discrepancy is
    confirmed, an adjustment to the invoice amount.

    Response deadline: 10 business days.

    Best regards,
    Receiving Department
    """,
]
