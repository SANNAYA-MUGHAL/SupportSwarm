# SupportSwarm

**SupportSwarm** is an enterprise-grade AI customer support and product intelligence platform. It orchestrates autonomous AI agent swarms to automate multi-channel ticket triage, conduct deep issue investigations, streamline human-in-the-loop approvals, and synthesize real-time customer feedback into actionable product opportunities.

---

## 🚀 Key Features

- **Omnichannel Support Hub**: Unified management of customer issues originating from email, web chat, voice calls, and direct portal submissions.
- **Autonomous Agent Swarms**: Purpose-built AI agents for automated classification, triage, root-cause investigation, and drafting responses.
- **Dynamic Ticket State Machine**: Robust ticket lifecycle management with strict state transition enforcement, SLA tracking, and complete audit logging.
- **Voice Transcription & Entity Extraction**: Audio processing pipeline extracting customer sentiment, entities, and key context from support recordings.
- **Incident & Bug Linkage**: Seamless escalation pathways connecting customer complaints directly to engineering bug reports and incident alerts.
- **Product Intelligence Engine**: Automatic extraction of feature requests, usability gaps, and customer quotes grouped into high-impact product opportunities.
- **Enterprise Security & Governance**: Role-based access control (RBAC), organization multi-tenancy, PII masking, and immutable audit trails.

---

## 🛠️ Tech Stack

### Backend
- **FastAPI**: Asynchronous Python REST API.
- **SQLAlchemy 2.0 & aiosqlite / PostgreSQL**: Fully async database layer.
- **Pydantic v2**: Strict schema validation and serialization.
- **PyJWT & Passlib / bcrypt**: Secure authentication and RBAC.
- **Pytest**: Comprehensive test suite covering state transitions, authorization, and workflows.

### Frontend
- **Next.js 14 (App Router)**: Modern React framework.
- **Tailwind CSS**: Utility-first styling with modern dark/light mode aesthetics.
- **Lucide React**: Clean icons.
- **Recharts**: Operational metrics and analytics visualization.

---

## 🏁 Quickstart

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or pnpm

### 1. Installation
Run the automated Makefile command to set up the backend virtual environment and install frontend packages:
```bash
make install
```

### 2. Database Seeding
Seed the database with sample organizations, agents, customers, and tickets:
```bash
make seed
```

### 3. Running the Application
Start the backend server (FastAPI on `http://localhost:8000`):
```bash
make run-backend
```

Start the frontend application (Next.js on `http://localhost:3000`):
```bash
make run-frontend
```

### 4. Running Tests
Run the complete backend test suite:
```bash
make test
```
