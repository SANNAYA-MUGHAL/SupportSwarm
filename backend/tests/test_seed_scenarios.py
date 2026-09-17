import pytest
from sqlalchemy import select, func
from app.models import (
    Customer, Ticket, KnowledgeArticle, ProductOpportunity, Incident, BugReport
)
from app.seed.seed_data import seed_database
from app.seed.scenarios import DemonstrationScenarios

@pytest.mark.asyncio
async def test_seed_database_execution_and_counts(db_session):
    # Run seed function
    await seed_database(db_session)

    # 1. Verify Customers >= 50
    cust_count = (await db_session.execute(select(func.count(Customer.id)))).scalar()
    assert cust_count >= 50, f"Expected >= 50 customers, got {cust_count}"

    # 2. Verify Tickets >= 100
    ticket_count = (await db_session.execute(select(func.count(Ticket.id)))).scalar()
    assert ticket_count >= 100, f"Expected >= 100 tickets, got {ticket_count}"

    # 3. Verify Knowledge Articles >= 20
    article_count = (await db_session.execute(select(func.count(KnowledgeArticle.id)))).scalar()
    assert article_count >= 20, f"Expected >= 20 articles, got {article_count}"

    # 4. Verify Product Opportunities >= 5
    opp_count = (await db_session.execute(select(func.count(ProductOpportunity.id)))).scalar()
    assert opp_count >= 5, f"Expected >= 5 opportunities, got {opp_count}"

    # 5. Verify Incidents >= 3
    inc_count = (await db_session.execute(select(func.count(Incident.id)))).scalar()
    assert inc_count >= 3, f"Expected >= 3 incidents, got {inc_count}"

    # 6. Verify Bug Reports exist
    bug_count = (await db_session.execute(select(func.count(BugReport.id)))).scalar()
    assert bug_count >= 3, f"Expected >= 3 bug reports, got {bug_count}"

@pytest.mark.asyncio
async def test_demonstration_scenarios(db_session):
    await seed_database(db_session)

    # Scenario A: Payment captured but order missing
    scen_a = await DemonstrationScenarios.get_scenario_a_data(db_session)
    assert scen_a["incident"] is not None
    assert scen_a["incident"].incident_number == "INC-101"
    assert scen_a["incident"].severity == "S1"
    assert scen_a["bug_report"] is not None
    assert scen_a["product_opportunity"] is not None

    # Scenario B: Refund delay
    scen_b = await DemonstrationScenarios.get_scenario_b_data(db_session)
    assert scen_b["ticket"] is not None

    # Scenario C: OTP not received (Regional)
    scen_c = await DemonstrationScenarios.get_scenario_c_data(db_session)
    assert scen_c["incident"] is not None
    assert scen_c["incident"].incident_number == "INC-102"
    assert "Punjab" in scen_c["region"]

    # Scenario D: Discount code misunderstanding
    scen_d = await DemonstrationScenarios.get_scenario_d_data(db_session)
    assert scen_d["opportunity"] is not None
    assert scen_d["opportunity"].category == "discount_code"
