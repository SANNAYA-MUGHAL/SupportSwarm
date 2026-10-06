'use client';

import React from 'react';
import { BookOpen } from 'lucide-react';
import { PhasePlaceholder } from '@/components/common/PhasePlaceholder';

export default function KnowledgePage() {
  return (
    <PhasePlaceholder
      phaseNumber={4}
      title="Knowledge Base & Similar Case Retrieval"
      subtitle="Hybrid vector + BM25 search over past resolutions, policies, and operating manuals"
      description="The Knowledge Base & Retrieval module powers the Technical Investigation Agent. It performs similarity matching across 500+ historical support tickets, merchant clearing policies, and bank timelines to provide verified answers with citation links."
      scenarioTag="Scenario B & C: Policy & Gateway Diagnostics"
      icon={BookOpen}
      features={[
        'Hybrid lexical and semantic retrieval (BM25 + OpenAI text-embedding-3-small)',
        'Historical ticket resolution matching with confidence scores',
        'Standard Operating Procedure (SOP) retrieval for refund and checkout failures',
        'Policy citation generator preventing hallucinated customer commitments',
      ]}
    />
  );
}
