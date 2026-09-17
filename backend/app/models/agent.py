from sqlalchemy import Column, String, Integer, Float, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

class Agent(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agents"

    name = Column(String(50), unique=True, index=True, nullable=False)  # intake, classification, investigation, etc.
    display_name = Column(String(100), nullable=False)
    system_prompt = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    max_daily_budget_usd = Column(Float, default=50.0, nullable=False)
    current_spend_usd = Column(Float, default=0.0, nullable=False)

    runs = relationship("AgentRun", back_populates="agent", cascade="all, delete-orphan")

class AgentRun(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agent_runs"

    agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_id = Column(String(36), ForeignKey("tickets.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(50), default="success", nullable=False)  # running, success, failed
    model_name = Column(String(100), default="hermes-3-llama-3.1", nullable=False)
    prompt_version = Column(String(50), default="v1.0.0", nullable=False)
    input_payload_json = Column(JSON, default=dict, nullable=False)
    output_payload_json = Column(JSON, default=dict, nullable=False)
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_cost_usd = Column(Float, default=0.0, nullable=False)
    confidence = Column(Float, default=0.95, nullable=False)
    execution_time_ms = Column(Integer, default=150, nullable=False)
    error_message = Column(Text, nullable=True)

    agent = relationship("Agent", back_populates="runs")
    tasks = relationship("AgentTask", back_populates="agent_run", cascade="all, delete-orphan")
    outputs = relationship("AgentOutput", back_populates="agent_run", cascade="all, delete-orphan")

class AgentTask(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agent_tasks"

    agent_run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    task_name = Column(String(100), nullable=False)
    status = Column(String(50), default="completed", nullable=False)
    assigned_to_agent_id = Column(String(36), ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    dependencies_json = Column(JSON, default=list, nullable=False)

    agent_run = relationship("AgentRun", back_populates="tasks")

class AgentOutput(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "agent_outputs"

    agent_run_id = Column(String(36), ForeignKey("agent_runs.id", ondelete="CASCADE"), nullable=False, index=True)
    output_type = Column(String(50), nullable=False)  # classification, investigation_report, draft_reply, incident_cluster
    structured_json = Column(JSON, nullable=False)

    agent_run = relationship("AgentRun", back_populates="outputs")
