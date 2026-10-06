'use client';

import React from 'react';
import { Bot } from 'lucide-react';
import { PhasePlaceholder } from '@/components/common/PhasePlaceholder';

export default function AgentsPage() {
  return (
    <PhasePlaceholder
      phaseNumber={5}
      title="Agent Orchestration & Activity Center"
      subtitle="Supervise specialized AI agents: Intake, Investigation, Approvals, Incident Detection, and Product Mining"
      description="The Agent Activity Center provides complete visibility into autonomous multi-agent reasoning traces. Inspect step-by-step tool executions, diagnostic API calls to payment gateways, and agent-to-agent coordination graphs."
      scenarioTag="Multi-Agent Pipeline Supervision"
      icon={Bot}
      features={[
        'Live execution telemetry across all 5 specialized AI agent roles',
        'Transparent tool-calling traces (Order API, Payment RPCs, Knowledge Base)',
        'Confidence thresholds and safety boundary overrides',
        'Token usage, latency, and model cost allocation metrics',
      ]}
    />
  );
}
