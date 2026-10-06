'use client';

import React from 'react';
import { CheckCircle2 } from 'lucide-react';
import { PhasePlaceholder } from '@/components/common/PhasePlaceholder';

export default function ApprovalsPage() {
  return (
    <PhasePlaceholder
      phaseNumber={5}
      title="Approvals & Human-in-the-Loop Queue"
      subtitle="Strict human approval gates for outbound customer communications, refunds, and sensitive actions"
      description="The Human-in-the-Loop Queue ensures no AI agent takes unilateral irreversible action. Support leads and agents review, edit, approve, or reject proposed customer responses, refund authorizations, and escalations with full audit logging."
      scenarioTag="Human Controlled Governance"
      icon={CheckCircle2}
      features={[
        'Outbound response draft review with side-by-side verification notes',
        'Financial action gates (refund approvals, coupon grants, credit notes)',
        'Diff preview showing AI suggestions vs human edits',
        'One-click batch approval with role-based signing',
      ]}
    />
  );
}
