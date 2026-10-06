'use client';

import React from 'react';
import { Mic } from 'lucide-react';
import { PhasePlaceholder } from '@/components/common/PhasePlaceholder';

export default function VoicePage() {
  return (
    <PhasePlaceholder
      phaseNumber={3}
      title="Voice Console & Multimodal Triage"
      subtitle="Bilingual speech-to-text, audio waveform player, intent classification & sentiment analysis"
      description="The Voice Console provides dedicated audio inspection for customer voice notes. In Phase 3, it processes raw audio through OpenAI Whisper, provides Urdu/English transcription, extracts order and transaction entities, and generates automated triage classifications."
      scenarioTag="Scenario B: Voice Note Urdu refund query"
      icon={Mic}
      features={[
        'Whisper speech-to-text with bilingual Urdu/English support',
        'Audio waveform player with synchronized transcription highlighting',
        'Automated entity extraction (Order IDs, Transaction IDs, amounts in PKR)',
        'Confidence scoring and sentiment detection (frustration, anger, urgency)',
      ]}
    />
  );
}
