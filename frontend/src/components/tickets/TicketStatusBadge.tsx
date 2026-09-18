import React from 'react';
import { TicketStatus } from '@/types/ticket';

const STATUS_CONFIG: Record<TicketStatus, { label: string; bg: string; text: string; dot: string }> = {
  new: {
    label: 'New',
    bg: 'bg-sky-50 border-sky-200',
    text: 'text-sky-700',
    dot: 'bg-sky-500',
  },
  triaged: {
    label: 'Triaged',
    bg: 'bg-slate-100 border-slate-200',
    text: 'text-slate-700',
    dot: 'bg-slate-500',
  },
  investigating: {
    label: 'Investigating',
    bg: 'bg-indigo-50 border-indigo-200',
    text: 'text-indigo-700',
    dot: 'bg-indigo-500 animate-pulse',
  },
  waiting_for_approval: {
    label: 'Waiting for Approval',
    bg: 'bg-amber-50 border-amber-200',
    text: 'text-amber-800',
    dot: 'bg-amber-500',
  },
  waiting_for_customer: {
    label: 'Waiting for Customer',
    bg: 'bg-purple-50 border-purple-200',
    text: 'text-purple-700',
    dot: 'bg-purple-500',
  },
  waiting_for_internal_team: {
    label: 'Waiting for Team',
    bg: 'bg-teal-50 border-teal-200',
    text: 'text-teal-800',
    dot: 'bg-teal-500',
  },
  resolved: {
    label: 'Resolved',
    bg: 'bg-emerald-50 border-emerald-200',
    text: 'text-emerald-700',
    dot: 'bg-emerald-500',
  },
  closed: {
    label: 'Closed',
    bg: 'bg-slate-100 border-slate-300',
    text: 'text-slate-600',
    dot: 'bg-slate-400',
  },
};

export function TicketStatusBadge({ status }: { status: TicketStatus | string }) {
  const config = STATUS_CONFIG[status as TicketStatus] || {
    label: status.replace(/_/g, ' '),
    bg: 'bg-slate-100 border-slate-200',
    text: 'text-slate-700',
    dot: 'bg-slate-400',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-semibold border ${config.bg} ${config.text}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
      <span>{config.label}</span>
    </span>
  );
}
