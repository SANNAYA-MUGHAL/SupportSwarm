from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Ticket, Incident, BugReport, ProductOpportunity, ApprovalRequest

class DemonstrationScenarios:
    @staticmethod
    async def get_scenario_a_data(db: AsyncSession) -> Dict[str, Any]:
        """
        Scenario A: Payment captured but order missing
        Five customers report the same problem within thirty minutes.
        Expected: High severity incident (INC-101), bug report (ENG-4892),
        product opportunity evidence, and draft responses.
        """
        inc_res = await db.execute(select(Incident).where(Incident.incident_number == "INC-101"))
        incident = inc_res.scalar_one_or_none()

        bug_res = await db.execute(select(BugReport).where(BugReport.incident_id == (incident.id if incident else None)))
        bug = bug_res.scalar_one_or_none()

        opp_res = await db.execute(select(ProductOpportunity).where(ProductOpportunity.category == "payment_pending"))
        opp = opp_res.scalar_one_or_none()

        return {
            "scenario": "Scenario A: Payment captured but order missing",
            "incident": incident,
            "bug_report": bug,
            "product_opportunity": opp,
            "pattern": "5 customers reported payment captured without order within 30 minutes"
        }

    @staticmethod
    async def get_scenario_b_data(db: AsyncSession) -> Dict[str, Any]:
        """
        Scenario B: Refund delay
        Customer reports refund has not arrived.
        Expected: Distinguishes merchant vs bank processing, matches article,
        drafts safe response without unsupported promise.
        """
        t_res = await db.execute(
            select(Ticket)
            .join(Ticket.classification)
            .where(Ticket.status == "waiting_for_approval")
            .limit(1)
        )
        ticket = t_res.scalar_one_or_none()
        return {
            "scenario": "Scenario B: Refund delay",
            "ticket": ticket,
            "rule": "Distinguish merchant vs bank delay; no unsupported promises"
        }

    @staticmethod
    async def get_scenario_c_data(db: AsyncSession) -> Dict[str, Any]:
        """
        Scenario C: OTP not received
        Multiple customers from same region report missing OTP messages.
        Expected: Regional incident INC-102, mock notification service failure identified.
        """
        inc_res = await db.execute(select(Incident).where(Incident.incident_number == "INC-102"))
        incident = inc_res.scalar_one_or_none()
        return {
            "scenario": "Scenario C: OTP not received (Regional)",
            "incident": incident,
            "region": "Punjab",
            "affected_service": "notification_svc"
        }

    @staticmethod
    async def get_scenario_d_data(db: AsyncSession) -> Dict[str, Any]:
        """
        Scenario D: Discount code misunderstanding
        UX/Knowledge problem rather than technical bug.
        Expected: Product opportunity for clearer checkout messaging.
        """
        opp_res = await db.execute(
            select(ProductOpportunity).where(ProductOpportunity.category == "discount_code")
        )
        opp = opp_res.scalar_one_or_none()
        return {
            "scenario": "Scenario D: Discount code misunderstanding",
            "opportunity": opp,
            "resolution_type": "knowledge_and_ux_clarification"
        }
