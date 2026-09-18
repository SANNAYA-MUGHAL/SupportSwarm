import React from 'react';
import { MessageSquare, Mic, Mail, FileText, Phone } from 'lucide-react';
import { TicketChannel } from '@/types/ticket';

export function ChannelBadge({ channel }: { channel: TicketChannel | string }) {
  let Icon = MessageSquare;
  let label = 'Web Chat';
  let style = 'text-slate-600 bg-slate-100';

  if (channel === 'voice_note') {
    Icon = Mic;
    label = 'Voice Note';
    style = 'text-indigo-700 bg-indigo-50 border-indigo-200';
  } else if (channel === 'email') {
    Icon = Mail;
    label = 'Email';
    style = 'text-sky-700 bg-sky-50 border-sky-200';
  } else if (channel === 'support_form') {
    Icon = FileText;
    label = 'Form';
    style = 'text-emerald-700 bg-emerald-50 border-emerald-200';
  } else if (channel === 'whatsapp') {
    Icon = Phone;
    label = 'WhatsApp';
    style = 'text-green-700 bg-green-50 border-green-200';
  }

  return (
    <span className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-medium border ${style}`}>
      <Icon className="w-3 h-3" />
      <span>{label}</span>
    </span>
  );
}
