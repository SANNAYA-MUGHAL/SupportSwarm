'use client';

import React from 'react';
import { Users } from 'lucide-react';
import { PhasePlaceholder } from '@/components/common/PhasePlaceholder';

export default function TeamPage() {
  return (
    <PhasePlaceholder
      phaseNumber={5}
      title="Team & Role-Based Access Control (RBAC)"
      subtitle="Manage organization members, seat allocation, operational roles, and queue assignments"
      description="The Team & RBAC console allows administrators to provision agents, configure permission boundaries (Admin, Support Lead, Support Agent, Viewer), assign support tiers, and audit seat utilization across the organization."
      scenarioTag="Enterprise Identity & Governance"
      icon={Users}
      features={[
        'Role-based permission matrix (Admin, Support Lead, Agent, Viewer)',
        'Agent capacity and queue routing rules based on language and skill tier',
        'Organization invite management with magic link generation',
        'Multi-tenant domain whitelisting and SAML SSO readiness',
      ]}
    />
  );
}
