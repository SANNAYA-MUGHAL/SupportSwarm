import React from 'react';
import { TicketSeverity } from '@/types/ticket';

export function SeverityBadge({ severity }: { severity?: TicketSeverity | string }) {
  if (!severity) return null;

  const s = severity.toUpperCase();
  let color = 'bg-slate-100 text-slate-700 border-slate-200';
  let label = s;

  if (s === 'S1') {
    color = 'bg-rose-100 text-rose-800 border-rose-300';
    label = 'S1 Critical';
  } else if (s === 'S2') {
    color = 'bg-amber-100 text-amber-800 border-amber-300';
    label = 'S2 High';
  } else if (s === 'S3') {
    color = 'bg-blue-100 text-blue-800 border-blue-200';
    label = 'S3 Medium';
  } else if (s === 'S4') {
    color = 'bg-slate-100 text-slate-700 border-slate-200';
    label = 'S4 Low';
  }

  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-bold border ${color}`}>
      {label}
    </span>
  );
}
