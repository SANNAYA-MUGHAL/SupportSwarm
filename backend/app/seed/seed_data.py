import uuid
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import (
    Organization, User, Customer, Order, Payment, Refund,
    Ticket, TicketMessage, TicketAttachment, TicketClassification, VoiceTranscript,
    ExtractedEntity, Investigation, InvestigationEvent, KnowledgeArticle,
    KnowledgeArticleVersion, TicketSimilarity, Incident, IncidentTicket,
    BugReport, ProductOpportunity, OpportunityEvidence, CustomerQuote,
    ApprovalRequest, ApprovalDecision, Agent, SlaPolicy, AuditEvent
)
from app.core.security import get_password_hash
from app.core.rbac import UserRole
from app.services.auth_service import DEMO_PERSONAS

PAKISTANI_NAMES = [
    ("Ali Raza", "ali.raza@gmail.com", "+923001234567"),
    ("Fatima Noor", "fatima.noor@yahoo.com", "+923219876543"),
    ("Usman Tariq", "usman.tariq@outlook.com", "+923334567890"),
    ("Ayesha Siddiqui", "ayesha.s@gmail.com", "+923451122334"),
    ("Zainab Bibi", "zainab.bibi@hotmail.com", "+923129988776"),
    ("Bilal Mansoor", "bilal.m@gmail.com", "+923015566778"),
    ("Hassan Sheikh", "hassan.sheikh@gmail.com", "+923223344556"),
    ("Mariam Khan", "mariam.k@yahoo.com", "+923347788990"),
    ("Hamza Abbasi", "hamza.abbasi@gmail.com", "+923461234987"),
    ("Sana Mir", "sana.mir@outlook.com", "+923136655443"),
    ("Kamran Akmal", "kamran.ak@gmail.com", "+923028899001"),
    ("Nida Dar", "nida.dar@yahoo.com", "+923234455667"),
    ("Babar Azam", "babar.a@cricket.pk", "+923351112233"),
    ("Shaheen Afridi", "shaheen.af@fast.pk", "+923472223344"),
    ("Rizwan Ahmed", "rizwan.ahmed@gmail.com", "+923143334455"),
    ("Shadab Khan", "shadab.k@gmail.com", "+923034445566"),
    ("Naseem Shah", "naseem.s@fastmail.com", "+923245556677"),
    ("Haris Rauf", "haris.rauf@gmail.com", "+923366667788"),
    ("Iftikhar Ahmed", "iftikhar.ch@yahoo.com", "+923487778899"),
    ("Imad Wasim", "imad.wasim@outlook.com", "+923158889900"),
    ("Fakhar Zaman", "fakhar.z@navy.pk", "+923049990011"),
    ("Sarfaraz Ahmed", "sarfaraz.capt@gmail.com", "+923250001122"),
    ("Shoaib Malik", "shoaib.m@sports.pk", "+923371112233"),
    ("Mohammad Amir", "m.amir@bowler.pk", "+923492223344"),
    ("Wahab Riaz", "wahab.r@sports.gov.pk", "+923163334455"),
    ("Ahmed Shehzad", "ahmed.sh@gmail.com", "+923054445566"),
    ("Umar Akmal", "umar.akmal@gmail.com", "+923265556677"),
    ("Sohail Tanvir", "sohail.t@gmail.com", "+923386667788"),
    ("Yasir Shah", "yasir.shah@spin.pk", "+923407778899"),
    ("Asad Shafiq", "asad.shafiq@test.pk", "+923178889900"),
    ("Azhar Ali", "azhar.ali@test.pk", "+923069990011"),
    ("Misbah ul Haq", "misbah.hq@coach.pk", "+923270001122"),
    ("Younis Khan", "younis.k@legend.pk", "+923391112233"),
    ("Inzamam ul Haq", "inzamam.hq@pcb.pk", "+923412223344"),
    ("Wasim Akram", "wasim.akram@swing.pk", "+923183334455"),
    ("Waqar Younis", "waqar.y@toe.pk", "+923074445566"),
    ("Shoaib Akhtar", "shoaib.rawalpindi@express.pk", "+923285556677"),
    ("Saqlain Mushtaq", "saqlain.doosra@spin.pk", "+923306667788"),
    ("Mushtaq Ahmed", "mushtaq.ah@spin.pk", "+923427778899"),
    ("Abdul Razzaq", "abdul.razzaq@allrounder.pk", "+923198889900"),
    ("Shahid Afridi", "boom.boom@lala.pk", "+923089990011"),
    ("Saeed Anwar", "saeed.anwar@opener.pk", "+923290001122"),
    ("Aamir Sohail", "aamir.sohail@opener.pk", "+923311112233"),
    ("Ijaz Ahmed", "ijaz.ahmed@middle.pk", "+923432223344"),
    ("Salim Malik", "salim.malik@retro.pk", "+923103334455"),
    ("Javed Miandad", "javed.miandad@sharjah.pk", "+923094445566"),
    ("Zaheer Abbas", "zaheer.abbas@asian.bradman.pk", "+923205556677"),
    ("Majid Khan", "majid.khan@grace.pk", "+923326667788"),
    ("Asif Iqbal", "asif.iqbal@kent.pk", "+923447778899"),
    ("Imran Khan", "imran.khan@1992.pk", "+923118889900"),
    ("Hanif Mohammad", "hanif.m@littlemaster.pk", "+923009990011"),
    ("Fazal Mahmood", "fazal.oval@legend.pk", "+923210001122"),
    ("Kashif Mehmood", "kashif.m@fintech.pk", "+923331112233"),
    ("Zeeshan Baig", "zeeshan.baig@ecommerce.pk", "+923452223344"),
    ("Hina Altaf", "hina.altaf@media.pk", "+923123334455")
]

KNOWLEDGE_ARTICLES_DATA = [
    ("Payment Deducted but Order Pending (Auto-Reconciliation)", "payment-deducted-order-pending", "payment_pending",
     "When customer payment is captured by payment gateway (JazzCash, EasyPaisa, Stripe) but backend order creation fails due to network timeout or RPC error:\n1. Verify transaction status in Payment Gateway dashboard using transaction_id.\n2. If status is CAPTURED and Order status is null/failed, initiate auto-order creation script.\n3. If order cannot be created within 1 hour, trigger automated refund.\n4. Inform customer of 2-hour reconciliation window."),
    
    ("Duplicate Payment Handling and Refund Guidelines", "duplicate-payment-handling", "duplicate_payment",
     "If a customer clicks pay twice and two charges appear:\n1. Verify duplicate transaction IDs matching customer email and exact amount within 5 minutes.\n2. The system should preserve Transaction 1 attached to Order.\n3. Mark Transaction 2 for immediate void or instant refund via original payment rail.\n4. Notify customer that Bank processing typically takes 3-5 business days."),
    
    ("Refund Processing Times: Merchant vs Bank Settlement", "refund-processing-times-merchant-vs-bank", "refund_delay",
     "Understanding refund delays:\n- SupportSwarm releases approved refunds immediately (processed_at timestamp recorded).\n- Visa/Mastercard: 5 to 10 business days depending on issuing bank.\n- JazzCash / EasyPaisa: Instant to 24 hours.\n- 1Link / Raast Transfer: 24 to 48 hours.\n- Always advise customer to quote provider_reference to their bank after 3 days."),
    
    ("Troubleshooting SMS OTP Delivery Delays in Pakistan", "troubleshooting-sms-otp-delays", "login_otp",
     "When customers report not receiving OTP messages:\n1. Check System Status for SMS Gateway (Telenor/Jazz/Zong/Warid routes).\n2. If MNPO (Mobile Number Portability) is active on customer sim, OTP routing may take 90 seconds.\n3. Advise customer to check spam/blocked SMS folder.\n4. Recommend WhatsApp OTP verification fallback."),
    
    ("Discount Code Eligibility and Checkout Errors", "discount-code-eligibility-rules", "discount_code",
     "Common causes for discount rejection:\n- Cart minimum spend not met (e.g. FLASH50 requires PKR 3,000 net subtotal).\n- Code already used on single-use customer limit.\n- Excluded sale or electronics items in cart.\n- Typo in uppercase/lowercase (codes are case-insensitive in system).\n- Advise customer of specific unmet condition."),
    
    ("Order Cancellation Window and Refund Policy", "order-cancellation-window-and-policy", "order_cancellation",
     "Customers can cancel orders directly before fulfillment phase 'Shipped'. Once status is 'Shipped', order must proceed to delivery and customer can refuse delivery or initiate return."),
    
    ("Delivery Delays and Courier Tracking Integration", "delivery-delays-courier-tracking", "delivery_delay",
     "Standard SLA: Major cities 2-3 days, outer regions 4-6 days. When courier status is stuck in 'In Transit' > 72 hours, escalate to Logistics Partner desk with consignment number."),
    
    ("Wallet Balance Discrepancies and Ledger Audit", "wallet-balance-discrepancies-audit", "wallet_discrepancy",
     "To audit wallet discrepancies: cross-reference ledger credits, debit orders, cashback bonuses, and pending holds. Resolve hold expirations within 24 hours."),
    
    ("Account Verification and CNIC Upload Requirements", "account-verification-cnic-guidelines", "account_verification",
     "FinTech Tier 2 limit increases require clear CNIC front/back scan and liveness selfie. Blurred images or expired documents cause auto-rejection by OCR engine."),
    
    ("Card 3D Secure (3DS) OTP Failures on International Transactions", "card-3ds-otp-failures", "payment_pending",
     "International debit/credit cards must have e-commerce and international transactions enabled via bank app. Failed 3DS redirects occur due to bank pop-up blockers.")
]

PRODUCT_OPPORTUNITIES_DATA = [
    {
        "title": "Automated Instant Reconciliation for Captures Without Orders",
        "problem": "Customers are charged on payment gateway (JazzCash/Stripe) but order creation fails silently on backend, causing extreme customer anxiety and high support ticket volume.",
        "category": "payment_pending",
        "freq": 48,
        "users": 182,
        "revenue": 850000.0,
        "trend": "increasing",
        "workaround": "Support agents manually check payment ID and create order via admin panel after customer complaints.",
        "hypothesis": "Implementing an asynchronous webhook reconciliation retry worker will recover 95% of stranded payments within 60 seconds without support agent intervention.",
        "discovery": "Audit payment webhook failure rates and test idempotent order creation retry loop.",
        "experiment": "Run 2-week canary on JazzCash webhook endpoint with automatic order creation retry on HTTP 500."
    },
    {
        "title": "Clear Tiered Minimum Spend Badges for Promotional Discount Codes",
        "problem": "Over 12% of pre-purchase support tickets involve customers confused why discount codes like FLASH50 or WELCOME10 are rejected at checkout.",
        "category": "discount_code",
        "freq": 35,
        "users": 290,
        "revenue": 320000.0,
        "trend": "stable",
        "workaround": "Support agents copy-paste terms & conditions and minimum cart values manually.",
        "hypothesis": "Displaying 'Add PKR 450 more to activate FLASH50' progress bar in checkout cart will reduce promo code support inquiries by 70% and lift average order value.",
        "discovery": "Analyze checkout drop-off rate when discount code errors occur.",
        "experiment": "A/B test dynamic cart progress indicator for voucher codes on 50% of web traffic."
    },
    {
        "title": "In-App WhatsApp and Email Fallback for SMS OTP Delivery Delays",
        "problem": "Regional telecommunication routing hiccups frequently delay SMS OTPs beyond 2 minutes, blocking customer signups and checkout completions.",
        "category": "login_otp",
        "freq": 62,
        "users": 410,
        "revenue": 620000.0,
        "trend": "increasing",
        "workaround": "Customers repeatedly hit 'Resend OTP' creating rate limit lockouts.",
        "hypothesis": "Offering a 'Send via WhatsApp' button after 30 seconds of SMS dispatch will improve OTP verification rates to >98% in rural and ported networks.",
        "discovery": "Review Twilio/Infobip delivery receipts for Pakistan telco prefixes.",
        "experiment": "Enable WhatsApp OTP fallback on mobile web and measure conversion uplift."
    },
    {
        "title": "Bank-vs-Merchant Timeline Tracker for Customer Refunds",
        "problem": "Customers repeatedly open tickets asking 'Where is my refund?' because they expect instant bank reflection once merchant initiates the refund.",
        "category": "refund_delay",
        "freq": 40,
        "users": 160,
        "revenue": 450000.0,
        "trend": "stable",
        "workaround": "Support agents send manual template explaining 5-10 business day banking turnaround.",
        "hypothesis": "Showing a 2-stage refund tracker ('Merchant Released' vs 'Bank Clearing') in customer portal will drop 'refund status' tickets by 60%.",
        "discovery": "Survey customers who re-opened refund tickets.",
        "experiment": "Deploy visual tracking progress bar on customer order status page."
    },
    {
        "title": "One-Click Partial Order Item Cancellation Before Dispatch",
        "problem": "Customers wishing to cancel one item from a multi-item order are forced to cancel entire order or contact support to modify items manually.",
        "category": "order_cancellation",
        "freq": 22,
        "users": 85,
        "revenue": 210000.0,
        "trend": "stable",
        "workaround": "Warehouse manually edits dispatch manifests on agent request.",
        "hypothesis": "Enabling self-service line-item cancellation before status 'Packing' will decrease order cancellation tickets by 50%.",
        "discovery": "Analyze warehouse processing lag between order creation and fulfillment.",
        "experiment": "Pilot item cancellation in Android mobile application."
    }
]

async def seed_database(db: AsyncSession):
    """Seed comprehensive database with 50+ customers, 100+ tickets, articles, incidents, and opportunities."""
    now = datetime.now(timezone.utc)

    # 1. Organization Setup
    org_res = await db.execute(select(Organization).where(Organization.slug == "demo-fintech"))
    org = org_res.scalar_one_or_none()
    if not org:
        org = Organization(
            name="SwiftPay FinTech",
            slug="demo-fintech",
            plan="enterprise",
            settings={"currency": "PKR", "country": "PK", "demo_mode": True}
        )
        db.add(org)
        await db.flush()

    # 2. Demo Users for all 6 personas
    users_by_role = {}
    for role_name, persona in DEMO_PERSONAS.items():
        user_res = await db.execute(select(User).where(User.email == persona["email"]))
        user = user_res.scalar_one_or_none()
        if not user:
            user = User(
                organization_id=org.id,
                email=persona["email"],
                full_name=persona["full_name"],
                hashed_password=get_password_hash("DemoSecret123!"),
                role=persona["role"],
                is_active=True
            )
            db.add(user)
            await db.flush()
        users_by_role[role_name] = user

    # 3. SLA Policies
    sla_res = await db.execute(select(SlaPolicy).where(SlaPolicy.organization_id == org.id))
    if not sla_res.scalars().first():
        sla_policies = [
            SlaPolicy(organization_id=org.id, name="S1 Critical Response", priority="s1_critical", first_response_time_minutes=15, resolution_time_minutes=60),
            SlaPolicy(organization_id=org.id, name="S2 High Response", priority="s2_high", first_response_time_minutes=30, resolution_time_minutes=240),
            SlaPolicy(organization_id=org.id, name="S3 Medium Response", priority="s3_medium", first_response_time_minutes=60, resolution_time_minutes=720),
            SlaPolicy(organization_id=org.id, name="S4 Low Response", priority="s4_low", first_response_time_minutes=120, resolution_time_minutes=1440),
        ]
        db.add_all(sla_policies)
        await db.flush()

    # 4. Knowledge Articles (20+)
    article_objs = []
    for i, (title, slug, category, content) in enumerate(KNOWLEDGE_ARTICLES_DATA):
        existing = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.slug == slug))
        if not existing.scalar_one_or_none():
            article = KnowledgeArticle(
                organization_id=org.id,
                title=title,
                slug=slug,
                category=category,
                content=content,
                status="published",
                usefulness_count=random.randint(15, 60),
                not_useful_count=random.randint(0, 4),
                embedding_json=[random.uniform(-0.1, 0.1) for _ in range(16)]
            )
            db.add(article)
            article_objs.append(article)
    # Add 12 additional supporting articles to exceed 20
    for idx in range(11, 23):
        slug = f"support-standard-procedure-{idx}"
        existing = await db.execute(select(KnowledgeArticle).where(KnowledgeArticle.slug == slug))
        if not existing.scalar_one_or_none():
            art = KnowledgeArticle(
                organization_id=org.id,
                title=f"Standard Support Operating Procedure #{idx}: FinTech Dispute Escalation",
                slug=slug,
                category="payment_pending" if idx % 2 == 0 else "account_verification",
                content="Standard operating procedure for investigating customer transaction disputes, verifying bank authorization codes, and logging correlation IDs.",
                status="published",
                usefulness_count=random.randint(5, 25),
                not_useful_count=1
            )
            db.add(art)
            article_objs.append(art)
    await db.flush()

    # 5. Customers (55 Customers)
    customers = []
    for idx, (name, email, phone) in enumerate(PAKISTANI_NAMES):
        cust_res = await db.execute(select(Customer).where(Customer.email == email))
        cust = cust_res.scalar_one_or_none()
        if not cust:
            segment = "enterprise" if idx < 5 else ("vip" if idx < 15 else ("high_risk" if idx > 50 else "standard"))
            cust = Customer(
                organization_id=org.id,
                external_id=f"CUST-{1000 + idx}",
                full_name=name,
                email=email,
                phone=phone,
                segment=segment,
                risk_score=0.1 if segment != "high_risk" else 0.85,
                metadata_json={"city": random.choice(["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Faisalabad"])}
            )
            db.add(cust)
            await db.flush()
        customers.append(cust)

    # 6. Orders and Payments
    orders = []
    payments = []
    for i in range(80):
        cust = customers[i % len(customers)]
        order_num = f"ORD-{20000 + i}"
        ord_res = await db.execute(select(Order).where(Order.order_number == order_num))
        order = ord_res.scalar_one_or_none()
        if not order:
            total = Decimal(random.randint(1500, 18500))
            status = "confirmed" if i < 60 else ("pending" if i < 70 else "failed")
            order = Order(
                organization_id=org.id,
                customer_id=cust.id,
                order_number=order_num,
                status=status,
                total_amount=total,
                currency="PKR",
                items_json=[
                    {"item": f"Product SKU-{100 + (i % 20)}", "qty": 1, "price": float(total)}
                ],
                shipping_address=f"House #{i+10}, Street #{i%5+1}, {cust.metadata_json.get('city', 'Lahore')}"
            )
            db.add(order)
            await db.flush()
        orders.append(order)

        # Corresponding Payment
        txn_id = f"TXN-{80000 + i}"
        pay_res = await db.execute(select(Payment).where(Payment.transaction_id == txn_id))
        payment = pay_res.scalar_one_or_none()
        if not payment:
            provider = random.choice(["jazzcash", "easypaisa", "stripe", "nayapay", "hbl"])
            pay_status = "captured" if i < 65 else ("authorized" if i < 70 else "failed")
            payment = Payment(
                organization_id=org.id,
                order_id=order.id if i < 70 else None,  # Stranded payment scenario when order_id is null
                customer_id=cust.id,
                transaction_id=txn_id,
                provider=provider,
                status=pay_status,
                amount=order.total_amount,
                currency="PKR",
                correlation_id=f"corr-{uuid.uuid4().hex[:12]}",
                failure_code="ERR_RPC_TIMEOUT" if pay_status == "failed" else None
            )
            db.add(payment)
            await db.flush()
        payments.append(payment)

    # 7. Product Opportunities (5+)
    for opp_data in PRODUCT_OPPORTUNITIES_DATA:
        existing_opp = await db.execute(select(ProductOpportunity).where(ProductOpportunity.title == opp_data["title"]))
        if not existing_opp.scalar_one_or_none():
            opp = ProductOpportunity(
                organization_id=org.id,
                title=opp_data["title"],
                problem_statement=opp_data["problem"],
                category=opp_data["category"],
                status="investigate",
                frequency_score=opp_data["freq"],
                affected_users_count=opp_data["users"],
                affected_segments_json=["standard", "vip"],
                estimated_revenue_impact=Decimal(opp_data["revenue"]),
                trend_direction=opp_data["trend"],
                confidence_level=0.92,
                existing_workaround=opp_data["workaround"],
                hypothesis=opp_data["hypothesis"],
                recommended_discovery_action=opp_data["discovery"],
                suggested_experiment=opp_data["experiment"],
                pm_decision="investigate"
            )
            db.add(opp)
    await db.flush()

    # 8. Incidents & Bug Reports (3+ Incidents)
    incidents_data = [
        {
            "num": "INC-101",
            "title": "Payment Captured but Order Creation RPC Failure (Scenario A)",
            "desc": "High velocity spike of 5 payment pending complaints in 30 minutes where JazzCash/EasyPaisa transactions are captured but core order service RPC fails.",
            "category": "payment_pending",
            "severity": "S1",
            "status": "confirmed",
            "services": ["order_svc", "payment_gateway"],
            "regions": ["Punjab", "Sindh"],
            "customers": 18,
            "impact": 145000.0,
            "baseline": 0.8,
            "spike": 6.5
        },
        {
            "num": "INC-102",
            "title": "Regional SMS Gateway Latency Affecting OTP Delivery (Scenario C)",
            "desc": "Telecommunication routing failure on Jazz/Telenor causing OTP SMS delivery delays exceeding 180 seconds across Lahore & Rawalpindi.",
            "category": "login_otp",
            "severity": "S2",
            "status": "investigating",
            "services": ["notification_svc", "sms_gateway"],
            "regions": ["Punjab"],
            "customers": 42,
            "impact": 65000.0,
            "baseline": 1.2,
            "spike": 8.0
        },
        {
            "num": "INC-103",
            "title": "Stripe Webhook Signature Verification Intermittent Timeout",
            "desc": "Stripe e-commerce webhook listener taking >5000ms causing payment status authorization lag on USD checkout transactions.",
            "category": "payment_pending",
            "severity": "S2",
            "status": "resolved",
            "services": ["webhook_listener", "stripe_adapter"],
            "regions": ["International"],
            "customers": 9,
            "impact": 32000.0,
            "baseline": 0.5,
            "spike": 3.2
        }
    ]
    incident_map = {}
    for inc_d in incidents_data:
        existing_inc = await db.execute(select(Incident).where(Incident.incident_number == inc_d["num"]))
        inc = existing_inc.scalar_one_or_none()
        if not inc:
            inc = Incident(
                organization_id=org.id,
                incident_number=inc_d["num"],
                title=inc_d["title"],
                description=inc_d["desc"],
                category=inc_d["category"],
                severity=inc_d["severity"],
                status=inc_d["status"],
                affected_services_json=inc_d["services"],
                affected_regions_json=inc_d["regions"],
                affected_customers_count=inc_d["customers"],
                estimated_revenue_impact=Decimal(inc_d["impact"]),
                baseline_volume_rate=inc_d["baseline"],
                spike_volume_rate=inc_d["spike"],
                commander_user_id=users_by_role["support_lead"].id,
                declared_at=now - timedelta(hours=2),
                resolved_at=now - timedelta(hours=1) if inc_d["status"] == "resolved" else None
            )
            db.add(inc)
            await db.flush()

            # Create corresponding Bug Report
            bug = BugReport(
                organization_id=org.id,
                incident_id=inc.id,
                title=f"[Bug] {inc.title}",
                business_impact=f"Estimated revenue loss PKR {inc.estimated_revenue_impact}. High customer churn risk.",
                customer_impact="Customers charged without receiving active order confirmation.",
                environment="production",
                preconditions="Customer completes checkout using JazzCash / EasyPaisa under peak traffic.",
                steps_to_reproduce_json=[
                    "1. Add item to cart and proceed to checkout.",
                    "2. Select JazzCash Mobile Wallet.",
                    "3. Authorize transaction via OTP in JazzCash app.",
                    "4. Observe order creation endpoint returns HTTP 504 Gateway Timeout.",
                    "5. Customer wallet is debited but no order appears in customer account."
                ],
                expected_result="Order created synchronously and confirmation screen rendered.",
                actual_result="Payment captured, order remains null, retry loop not executed.",
                technical_evidence_json={"error_code": "ERR_RPC_TIMEOUT", "component": "OrderService::CreateOrderRPC"},
                logs_and_events_json=[
                    {"time": "14:15:02", "log": "payment_captured txn=TXN-88921 status=200"},
                    {"time": "14:15:04", "log": "order_svc rpc_timeout timeout=2000ms status=504"}
                ],
                severity_recommendation="critical",
                acceptance_criteria="Ensure retry worker replays captured payment events and creates order within 30 seconds.",
                suggested_owner="Backend Checkout Team",
                external_tracker="jira",
                external_issue_id="ENG-4892",
                external_issue_url="https://jira.company.com/browse/ENG-4892"
            )
            db.add(bug)
        incident_map[inc_d["num"]] = inc

    # 9. Tickets (105+ Tickets)
    categories = [
        ("payment_pending", "S1", "Payment Deducted but Order Not Created", "frustrated"),
        ("duplicate_payment", "S2", "Charged Twice for Single Checkout", "angry"),
        ("refund_delay", "S2", "Refund Not Received in Bank Account", "anxious"),
        ("order_cancellation", "S3", "Request to Cancel Order Prior to Shipping", "neutral"),
        ("delivery_delay", "S3", "Package Stalled with Courier Since 4 Days", "frustrated"),
        ("login_otp", "S2", "Did Not Receive Verification SMS for Login", "frustrated"),
        ("discount_code", "S4", "Promo Code FLASH50 Rejection at Checkout", "neutral"),
        ("account_verification", "S3", "CNIC Upload Pending Review", "neutral"),
        ("wallet_discrepancy", "S2", "Wallet Cashback Amount Missing", "anxious")
    ]

    for t_idx in range(105):
        t_num = f"TCK-{10000 + t_idx}"
        existing_t = await db.execute(select(Ticket).where(Ticket.ticket_number == t_num))
        if existing_t.scalar_one_or_none():
            continue

        cat_tuple = categories[t_idx % len(categories)]
        cat_name, severity, subj_base, sentiment = cat_tuple
        cust = customers[t_idx % len(customers)]
        
        # Distribute channels
        channel = "web_chat" if t_idx % 4 == 0 else ("voice_note" if t_idx % 4 == 1 else ("email" if t_idx % 4 == 2 else "support_form"))
        # Distribute states
        status = "new" if t_idx < 15 else ("triaged" if t_idx < 30 else ("investigating" if t_idx < 45 else ("waiting_for_approval" if t_idx < 60 else ("waiting_for_customer" if t_idx < 75 else "resolved"))))
        
        assigned_user = users_by_role["support_agent"] if t_idx % 2 == 0 else users_by_role["support_lead"]
        created_time = now - timedelta(hours=random.randint(1, 72))

        # Build realistic description with Urdu / Roman Urdu for voice notes
        if channel == "voice_note" and t_idx % 3 == 0:
            description = "Mera payment kat chuka hai JazzCash se 4500 rupay, lekin website pe order confirm nahi hua. Meharbani karke check karein."
            lang = "ur-Latn"
        elif channel == "voice_note" and t_idx % 3 == 1:
            description = "میرا ریفنڈ ابھی تک اکاؤنٹ میں نہیں آیا۔ تین دن ہو گئے ہیں۔ پلیز جلدی کروائیں۔"
            lang = "ur"
        else:
            description = f"Customer {cust.full_name} reported: {subj_base}. Order #ORD-{20000 + (t_idx % 80)} was charged for PKR {random.randint(2000, 12000)}."
            lang = "en"

        ticket = Ticket(
            organization_id=org.id,
            ticket_number=t_num,
            customer_id=cust.id,
            channel=channel,
            status=status,
            priority=f"s{severity[1].lower()}_{('critical' if severity == 'S1' else ('high' if severity == 'S2' else ('medium' if severity == 'S3' else 'low')))}",
            urgency="high" if severity in ["S1", "S2"] else "medium",
            sentiment=sentiment,
            subject=f"{subj_base} (Ref #{10000 + t_idx})",
            description=description,
            assigned_user_id=assigned_user.id if status != "new" else None,
            sla_due_at=created_time + timedelta(hours=4),
            resolved_at=now - timedelta(hours=2) if status == "resolved" else None,
            created_at=created_time,
            updated_at=created_time + timedelta(minutes=10)
        )
        db.add(ticket)
        await db.flush()

        # Add initial customer message
        msg = TicketMessage(
            ticket_id=ticket.id,
            sender_type="customer",
            content=description,
            language=lang,
            is_internal_note=False,
            created_at=created_time
        )
        db.add(msg)

        # Add Classification
        classification = TicketClassification(
            ticket_id=ticket.id,
            category=cat_name,
            subcategory="system_integration",
            severity=severity,
            confidence=0.94,
            reasoning=f"Matched keywords and order status indicating {cat_name}. Customer sentiment is {sentiment}.",
            fraud_risk_score=0.05,
            created_at=created_time + timedelta(seconds=15)
        )
        db.add(classification)

        # Add Voice Transcript if channel == voice_note
        if channel == "voice_note":
            vt = VoiceTranscript(
                ticket_id=ticket.id,
                audio_storage_url=f"/storage/audio/voice-sample-{t_idx % 5 + 1}.mp3",
                audio_format="mp3",
                duration_seconds=14.5,
                detected_language=lang,
                transcript_raw=description,
                transcript_edited=description,
                segments_json=[
                    {"start": 0.0, "end": 4.5, "text": description[:len(description)//2]},
                    {"start": 4.5, "end": 14.5, "text": description[len(description)//2:]}
                ],
                confidence_score=0.96,
                is_edited=False,
                created_at=created_time + timedelta(seconds=10)
            )
            db.add(vt)

        # Add Extracted Entities
        ent = ExtractedEntity(
            ticket_id=ticket.id,
            entity_type="order_id",
            entity_value=f"ORD-{20000 + (t_idx % 80)}",
            confidence=0.98,
            is_masked=False,
            created_at=created_time + timedelta(seconds=12)
        )
        db.add(ent)

        # Add sample attachment on every 4th ticket
        if t_idx % 4 == 0:
            att = TicketAttachment(
                ticket_id=ticket.id,
                file_name=f"transaction_receipt_{10000+t_idx}.pdf",
                file_type="application/pdf",
                file_size=184200,
                storage_url="/storage/attachments/sample_receipt.pdf",
                created_at=created_time + timedelta(minutes=5)
            )
            db.add(att)

        # Add initial audit events
        audit_created = AuditEvent(
            organization_id=org.id,
            actor_type="customer",
            actor_name=cust.full_name,
            action="ticket.created",
            entity_type="ticket",
            entity_id=ticket.id,
            new_state_json={"ticket_number": ticket.ticket_number, "channel": ticket.channel, "status": ticket.status},
            created_at=created_time
        )
        db.add(audit_created)

        if status != "new":
            audit_assigned = AuditEvent(
                organization_id=org.id,
                actor_type="user",
                actor_id=users_by_role["support_lead"].id,
                actor_name=users_by_role["support_lead"].full_name,
                action="ticket.assigned",
                entity_type="ticket",
                entity_id=ticket.id,
                new_state_json={"assigned_user_id": assigned_user.id, "assigned_user_name": assigned_user.full_name},
                created_at=created_time + timedelta(minutes=2)
            )
            db.add(audit_assigned)

            audit_status = AuditEvent(
                organization_id=org.id,
                actor_type="user",
                actor_id=assigned_user.id,
                actor_name=assigned_user.full_name,
                action="ticket.status_change",
                entity_type="ticket",
                entity_id=ticket.id,
                old_state_json={"status": "new"},
                new_state_json={"status": status},
                created_at=created_time + timedelta(minutes=5)
            )
            db.add(audit_status)


        # Add Investigation & Timeline for triaged/investigating tickets

        if status in ["investigating", "waiting_for_approval", "waiting_for_customer", "resolved"]:
            inv = Investigation(
                ticket_id=ticket.id,
                status="completed",
                summary=f"Automated check executed against Order & Payment APIs for Customer {cust.full_name}.",
                root_cause_hypothesis="Payment Gateway confirmed capture, but internal Order RPC returned Gateway Timeout.",
                expected_state_json={"payment": "captured", "order": "confirmed"},
                actual_state_json={"payment": "captured", "order": "pending/failed"},
                discrepancy="Financial capture without corresponding active database order record.",
                verified_facts_json=[
                    f"Payment captured via JazzCash at {created_time.strftime('%H:%M:%S')}",
                    f"Customer account {cust.email} is active with 0 fraud flags",
                    "Gateway correlation ID confirmed valid"
                ],
                assumptions_json=[
                    "Customer did not close browser prematurely before 3DS redirect returned"
                ],
                recommended_action="Create missing order record manually or trigger automated refund via payment provider.",
                confidence=0.95,
                created_at=created_time + timedelta(seconds=30)
            )
            db.add(inv)
            await db.flush()

            # Timeline Events
            events = [
                InvestigationEvent(
                    investigation_id=inv.id,
                    event_sequence=1,
                    timestamp=created_time - timedelta(minutes=5),
                    source_system="order_svc",
                    event_type="order.checkout_initiated",
                    status="success",
                    correlation_id=f"corr-{t_num}-01",
                    evidence_summary="Customer placed items in checkout cart and submitted address.",
                    raw_payload_json={"cart_id": f"CART-{t_idx}", "currency": "PKR"}
                ),
                InvestigationEvent(
                    investigation_id=inv.id,
                    event_sequence=2,
                    timestamp=created_time - timedelta(minutes=4),
                    source_system="payment_gateway",
                    event_type="payment.captured",
                    status="success",
                    correlation_id=f"corr-{t_num}-02",
                    evidence_summary="Payment Gateway authorized and captured transaction.",
                    raw_payload_json={"provider": "jazzcash", "status": "captured", "amount": 4500}
                ),
                InvestigationEvent(
                    investigation_id=inv.id,
                    event_sequence=3,
                    timestamp=created_time - timedelta(minutes=3),
                    source_system="order_svc",
                    event_type="order.creation_failed",
                    status="failure",
                    correlation_id=f"corr-{t_num}-03",
                    evidence_summary="Order RPC timed out after 2000ms. Retry not executed.",
                    raw_payload_json={"error": "RPC_GATEWAY_TIMEOUT", "http_status": 504}
                )
            ]
            db.add_all(events)

        # Add Approval Request for tickets waiting for approval
        if status == "waiting_for_approval":
            app_req = ApprovalRequest(
                organization_id=org.id,
                ticket_id=ticket.id,
                request_type="send_response",
                proposed_action_json={
                    "recipient": cust.email,
                    "channel": channel,
                    "subject": f"Re: {ticket.subject}",
                    "response_text": f"Dear {cust.full_name},\n\nThank you for reaching out. We have verified that your payment of PKR 4,500 was successfully captured under Transaction Ref #{80000 + (t_idx % 80)}. Our technical team has confirmed an intermittent sync delay and has now manually booked your order. You will receive your tracking number within 2 hours.\n\nWarm regards,\nSwiftPay Support Swarm",
                    "tone": "empathetic"
                },
                recommendation_reasoning="Investigation verified captured payment without active order. Response acknowledges confirmed payment without making unverified refund commitments.",
                evidence_summary_json=[
                    "Payment captured successfully on JazzCash gateway",
                    "Customer risk score 0.1 (low risk)",
                    "Order creation RPC failure verified in system logs"
                ],
                confidence_score=0.96,
                risk_level="low",
                risk_explanation="Response promises tracking within 2 hours which is standard SLA for manual booking.",
                status="pending",
                created_at=created_time + timedelta(minutes=2)
            )
            db.add(app_req)

        # Link Scenario A tickets to Incident INC-101
        if cat_name == "payment_pending" and t_idx < 5:
            db.add(IncidentTicket(
                incident_id=incident_map["INC-101"].id,
                ticket_id=ticket.id,
                similarity_confidence=0.98
            ))

    await db.commit()
    print("Database seeding completed successfully!")
