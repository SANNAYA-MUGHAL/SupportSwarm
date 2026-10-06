'use client';

import React from 'react';
import { Lightbulb } from 'lucide-react';
import { PhasePlaceholder } from '@/components/common/PhasePlaceholder';

export default function ProductIntelligencePage() {
  return (
    <PhasePlaceholder
      phaseNumber={7}
      title="Product Intelligence & Opportunity Mining"
      subtitle="Transforming high-frequency customer friction and support patterns into prioritized roadmap opportunities"
      description="The Product Opportunity Mining engine correlates hundreds of support tickets into strategic product opportunities. It quantifies business impact (lost revenue, churn risk, operational hours) and generates structured PRD briefs with customer evidence quotes."
      scenarioTag="Scenario D: Discount confusion converted to UX improvement"
      icon={Lightbulb}
      features={[
        'Pattern clustering across 100+ tickets into 5 prioritized opportunities',
        'Financial impact modeling (e.g. PKR 850,000 lost revenue from failed RPCs)',
        'Evidence synthesizer linking direct customer verbatims to product pain points',
        'One-click PRD / User Story generation for engineering and product teams',
      ]}
    />
  );
}
