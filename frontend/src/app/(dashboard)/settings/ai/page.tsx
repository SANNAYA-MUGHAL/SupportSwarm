'use client';

import React from 'react';
import { Cpu } from 'lucide-react';
import { PhasePlaceholder } from '@/components/common/PhasePlaceholder';

export default function AiSettingsPage() {
  return (
    <PhasePlaceholder
      phaseNumber={5}
      title="AI & Safety Settings"
      subtitle="Configure LLM model providers, hallucination guardrails, confidence gates, and safety filters"
      description="The AI & Safety configuration module establishes policy boundaries for all automated reasoning. Define acceptable confidence scores, prohibit unauthorized promises (e.g. guaranteeing refund dates before bank clearance), and select default model providers."
      scenarioTag="Enterprise Safety & Compliance"
      icon={Cpu}
      features={[
        'Strict policy boundary checks preventing hallucinated financial commitments',
        'Provider selection (OpenAI GPT-4o, Anthropic Claude 3.5 Sonnet, Local fallback)',
        'PII redaction and anonymization filters for sensitive customer records',
        'Human override escalation triggers for low-confidence agent outputs',
      ]}
    />
  );
}
