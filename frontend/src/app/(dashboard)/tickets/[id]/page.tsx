'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Clock,
  User as UserIcon,
  ShoppingBag,
  CreditCard,
  MessageSquare,
  ShieldAlert,
  Send,
  Lock,
  Mic,
  Activity,
  Check,
  ChevronRight,
  FileText,
  Sparkles,
  Bot
} from 'lucide-react';
import { ApiClient } from '@/lib/api-client';
import { TicketDetailResponse, TicketStatus } from '@/types/ticket';
import { TicketStatusBadge } from '@/components/tickets/TicketStatusBadge';
import { SeverityBadge } from '@/components/tickets/SeverityBadge';
import { ChannelBadge } from '@/components/tickets/ChannelBadge';
import { useAuth } from '@/lib/auth-context';
import { formatCurrency } from '@/lib/utils';

export default function TicketDetailPage() {
  const params = useParams();
  const router = useRouter();
  const ticketId = params.id as string;
  const { user } = useAuth();

  const [ticket, setTicket] = useState<TicketDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Message & Internal Note form
  const [noteContent, setNoteContent] = useState('');
  const [isInternalNote, setIsInternalNote] = useState(false);
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  // State Transition & Assignment
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);

  const fetchTicket = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const res = await ApiClient.get<TicketDetailResponse>(`/tickets/${ticketId}`);
      setTicket(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load ticket details.');
    } finally {
      setIsLoading(false);
    }
  }, [ticketId]);

  useEffect(() => {
    fetchTicket();
  }, [fetchTicket]);

  const handleStatusChange = async (targetStatus: string) => {
    setIsUpdatingStatus(true);
    try {
      await ApiClient.patch(`/tickets/${ticketId}/status`, {
        target_status: targetStatus,
        reason: `Manual status transition by ${user?.full_name}`,
      });
      await fetchTicket();
    } catch (err: any) {
      alert(err.message || 'Failed to update status.');
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleAssignSelf = async () => {
    if (!user) return;
    setIsAssigning(true);
    try {
      await ApiClient.patch(`/tickets/${ticketId}/assign`, {
        user_id: user.id,
      });
      await fetchTicket();
    } catch (err: any) {
      alert(err.message || 'Failed to assign ticket.');
    } finally {
      setIsAssigning(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteContent.trim()) return;

    setIsSendingMessage(true);
    try {
      await ApiClient.post(`/tickets/${ticketId}/messages`, {
        content: noteContent.trim(),
        is_internal_note: isInternalNote,
        language: 'en',
      });
      setNoteContent('');
      await fetchTicket();
    } catch (err: any) {
      alert(err.message || 'Failed to send message.');
    } finally {
      setIsSendingMessage(false);
    }
  };

  if (isLoading && !ticket) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-slate-500 font-medium">Loading ticket workspace...</p>
        </div>
      </div>
    );
  }

  if (error || !ticket) {
    return (
      <div className="p-8 max-w-xl mx-auto text-center space-y-4">
        <div className="w-12 h-12 rounded-2xl bg-rose-50 text-rose-600 flex items-center justify-center mx-auto border border-rose-200">
          <AlertCircle className="w-6 h-6" />
        </div>
        <h2 className="text-base font-bold text-slate-900">Ticket Not Found</h2>
        <p className="text-xs text-slate-500">{error || 'Unable to retrieve ticket.'}</p>
        <Link
          href="/tickets"
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Ticket Inbox</span>
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-5 max-w-7xl mx-auto">
      {/* Top Header & Breadcrumb */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            href="/tickets"
            className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition-colors shadow-xs"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono font-bold text-base text-indigo-600">
                {ticket.ticket_number}
              </span>
              <TicketStatusBadge status={ticket.status} />
              <SeverityBadge severity={ticket.classification?.severity || 'S3'} />
              <ChannelBadge channel={ticket.channel} />
              {ticket.reopened_count > 0 && (
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-900 border border-amber-300">
                  Reopened ({ticket.reopened_count}x)
                </span>
              )}
            </div>
            <h1 className="text-sm font-bold text-slate-900 mt-1 line-clamp-1">
              {ticket.subject}
            </h1>
          </div>
        </div>

        {/* Workflow State Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Assignee Control */}
          <div className="flex items-center gap-1.5">
            {ticket.assigned_user_id ? (
              <span className="text-xs px-2.5 py-1.5 rounded-xl bg-slate-100 text-slate-700 font-medium border border-slate-200 flex items-center gap-1.5">
                <UserIcon className="w-3.5 h-3.5 text-slate-500" />
                <span className="font-semibold text-slate-900">{ticket.assigned_user_name}</span>
              </span>
            ) : (
              <button
                onClick={handleAssignSelf}
                disabled={isAssigning}
                className="text-xs px-3 py-1.5 rounded-xl bg-indigo-50 hover:bg-indigo-100 text-indigo-700 font-semibold border border-indigo-200 transition-colors"
              >
                Assign to Me
              </button>
            )}
          </div>

          {/* Status Transition Selector */}
          <div className="flex items-center gap-1.5">
            <label className="text-xs font-medium text-slate-500">Status:</label>
            <select
              value={ticket.status}
              disabled={isUpdatingStatus}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="text-xs font-semibold bg-white border border-slate-300 rounded-xl px-3 py-1.5 text-slate-900 focus:outline-none focus:border-indigo-500 shadow-xs cursor-pointer capitalize"
            >
              <option value={ticket.status} disabled>
                Current: {ticket.status.replace(/_/g, ' ')}
              </option>
              {ticket.allowed_transitions.map((nextStatus) => (
                <option key={nextStatus} value={nextStatus}>
                  Move to: {nextStatus.replace(/_/g, ' ')}
                </option>
              ))}
            </select>
          </div>

          <button
            onClick={fetchTicket}
            className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition-colors shadow-xs"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-indigo-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* 3-Column Workspace Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Column: Customer, Order & Payment Telemetry (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          {/* Customer Profile Card */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <UserIcon className="w-4 h-4 text-indigo-600" />
                <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Customer Profile
                </h2>
              </div>
              <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-indigo-50 text-indigo-700 border border-indigo-200 capitalize">
                {ticket.customer.segment}
              </span>
            </div>

            <div>
              <p className="text-sm font-bold text-slate-900">{ticket.customer.full_name}</p>
              <p className="text-xs text-slate-500">{ticket.customer.email}</p>
              {ticket.customer.phone && (
                <p className="text-xs text-slate-500 mt-0.5">{ticket.customer.phone}</p>
              )}
            </div>

            <div className="pt-2 border-t border-slate-100 text-[11px] space-y-1.5 text-slate-600">
              <div className="flex justify-between">
                <span>Customer ID:</span>
                <span className="font-mono font-medium text-slate-900">
                  {ticket.customer.external_id || 'CUST-STD'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Risk Score:</span>
                <span
                  className={`font-semibold ${
                    ticket.customer.risk_score > 0.5 ? 'text-rose-600' : 'text-emerald-600'
                  }`}
                >
                  {(ticket.customer.risk_score * 100).toFixed(0)}% (
                  {ticket.customer.risk_score > 0.5 ? 'High Risk' : 'Healthy'})
                </span>
              </div>
              {ticket.customer.metadata_json?.city && (
                <div className="flex justify-between">
                  <span>Region / City:</span>
                  <span className="font-medium text-slate-900">
                    {ticket.customer.metadata_json.city}
                  </span>
                </div>
              )}
            </div>
          </div>

          {/* Linked Order Telemetry */}
          {ticket.order ? (
            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShoppingBag className="w-4 h-4 text-indigo-600" />
                  <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Order Telemetry
                  </h2>
                </div>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700 capitalize">
                  {ticket.order.status}
                </span>
              </div>

              <div>
                <p className="font-mono font-bold text-xs text-indigo-900">
                  {ticket.order.order_number}
                </p>
                <p className="text-xs font-semibold text-slate-900 mt-0.5">
                  {formatCurrency(ticket.order.total_amount, ticket.order.currency)}
                </p>
              </div>

              {ticket.order.items_json.length > 0 && (
                <div className="pt-2 border-t border-slate-100 text-[11px] space-y-1">
                  <span className="font-medium text-slate-500">Cart Items:</span>
                  {ticket.order.items_json.map((item, idx) => (
                    <div key={idx} className="flex justify-between text-slate-700">
                      <span className="truncate max-w-[140px]">{item.item}</span>
                      <span>x{item.qty}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-200 text-[11px] text-slate-500 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-slate-700">
                <ShoppingBag className="w-3.5 h-3.5" />
                <span>No Order Attached</span>
              </div>
              <p>No verified order record found matching this ticket.</p>
            </div>
          )}

          {/* Linked Payment Telemetry */}
          {ticket.payment ? (
            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CreditCard className="w-4 h-4 text-emerald-600" />
                  <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Payment Gateway
                  </h2>
                </div>
                <span
                  className={`px-1.5 py-0.5 rounded text-[10px] font-bold capitalize ${
                    ticket.payment.status === 'captured'
                      ? 'bg-emerald-50 text-emerald-700 border border-emerald-200'
                      : 'bg-amber-50 text-amber-800 border border-amber-200'
                  }`}
                >
                  {ticket.payment.status}
                </span>
              </div>

              <div>
                <p className="text-xs font-bold text-slate-900 capitalize">
                  {ticket.payment.provider}
                </p>
                <p className="font-mono text-[11px] text-slate-600 truncate mt-0.5">
                  Ref: {ticket.payment.transaction_id}
                </p>
              </div>

              <div className="pt-2 border-t border-slate-100 text-[11px] space-y-1.5 text-slate-600">
                <div className="flex justify-between">
                  <span>Charged:</span>
                  <span className="font-semibold text-slate-900">
                    {formatCurrency(ticket.payment.amount, ticket.payment.currency)}
                  </span>
                </div>
                {ticket.payment.correlation_id && (
                  <div className="flex justify-between">
                    <span>Correlation:</span>
                    <span className="font-mono text-[10px] text-slate-500 truncate max-w-[120px]">
                      {ticket.payment.correlation_id}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-200 text-[11px] text-slate-500 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-slate-700">
                <CreditCard className="w-3.5 h-3.5" />
                <span>No Payment Linked</span>
              </div>
              <p>No transaction record matched to this ticket.</p>
            </div>
          )}
        </div>

        {/* Middle Column: Conversation Stream & Message Box (6 cols) */}
        <div className="lg:col-span-6 space-y-4">
          {/* Customer Voice Recording Player if channel == voice_note */}
          {ticket.voice_transcript && (
            <div className="bg-indigo-50/60 p-4 rounded-2xl border border-indigo-200 space-y-2">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Mic className="w-4 h-4 text-indigo-700" />
                  <span className="text-xs font-bold text-indigo-950">Customer Voice Note</span>
                </div>
                <span className="text-[10px] font-semibold px-2 py-0.5 bg-indigo-100 text-indigo-800 rounded-full">
                  Lang: {ticket.voice_transcript.detected_language} • {(ticket.voice_transcript.confidence_score * 100).toFixed(0)}% Confidence
                </span>
              </div>

              <audio
                controls
                src={ticket.voice_transcript.audio_storage_url}
                className="w-full h-8 mt-1"
              >
                Your browser does not support audio playback.
              </audio>

              <div className="p-3 bg-white/90 rounded-xl border border-indigo-100 text-xs text-slate-800 leading-relaxed font-sans mt-2">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                  Whisper Transcript:
                </span>
                &quot;{ticket.voice_transcript.transcript_raw}&quot;
              </div>
            </div>
          )}

          {/* Conversation & Notes Stream */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between border-b border-slate-100 pb-3">
              <div className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-indigo-600" />
                <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                  Ticket Activity & Communications
                </h2>
              </div>
              <span className="text-[11px] text-slate-400">
                {ticket.messages.length} message(s)
              </span>
            </div>

            {/* Message List */}
            <div className="space-y-3.5 max-h-[520px] overflow-y-auto pr-1">
              {ticket.messages.map((m) => {
                const isCustomer = m.sender_type === 'customer';
                const isNote = m.is_internal_note;

                return (
                  <div
                    key={m.id}
                    className={`p-3.5 rounded-2xl text-xs leading-relaxed transition-all ${
                      isNote
                        ? 'bg-amber-50/80 border border-amber-200 text-amber-950'
                        : isCustomer
                        ? 'bg-slate-50 border border-slate-200 text-slate-800'
                        : 'bg-indigo-50/70 border border-indigo-200 text-indigo-950 ml-4'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <div className="flex items-center gap-1.5">
                        {isNote && <Lock className="w-3 h-3 text-amber-700" />}
                        <span className="font-bold text-[11px]">
                          {isNote
                            ? 'Internal Staff Note'
                            : isCustomer
                            ? ticket.customer.full_name
                            : m.sender_name || 'Support Agent'}
                        </span>
                        <span className="text-[10px] px-1 rounded bg-white/70 text-slate-500 font-medium">
                          {m.sender_type}
                        </span>
                      </div>
                      <span className="text-[10px] text-slate-400">
                        {new Date(m.created_at).toLocaleTimeString('en-PK', {
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </span>
                    </div>
                    <p className="whitespace-pre-wrap">{m.content}</p>
                  </div>
                );
              })}
            </div>

            {/* Compose Box */}
            <form onSubmit={handleSendMessage} className="pt-3 border-t border-slate-100 space-y-3">
              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setIsInternalNote(false)}
                  className={`text-xs font-semibold px-3 py-1.5 rounded-xl transition-all ${
                    !isInternalNote
                      ? 'bg-indigo-600 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  Reply to Customer
                </button>
                <button
                  type="button"
                  onClick={() => setIsInternalNote(true)}
                  className={`flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-xl transition-all ${
                    isInternalNote
                      ? 'bg-amber-500 text-white shadow-xs'
                      : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}
                >
                  <Lock className="w-3 h-3" />
                  <span>Internal Note</span>
                </button>
              </div>

              <div className="relative">
                <textarea
                  rows={3}
                  value={noteContent}
                  onChange={(e) => setNoteContent(e.target.value)}
                  placeholder={
                    isInternalNote
                      ? 'Write a private note visible only to support agents and leads...'
                      : 'Write a verified, empathetic response to the customer...'
                  }
                  className={`w-full text-xs p-3 rounded-xl border focus:outline-none focus:ring-1 transition-all ${
                    isInternalNote
                      ? 'bg-amber-50/40 border-amber-300 focus:border-amber-500 focus:ring-amber-500 text-amber-950 placeholder:text-amber-800/40'
                      : 'bg-slate-50 border-slate-200 focus:border-indigo-500 focus:ring-indigo-500 text-slate-900'
                  }`}
                />
              </div>

              <div className="flex items-center justify-between">
                <span className="text-[11px] text-slate-400">
                  {isInternalNote
                    ? '🔒 Private note (not sent to customer)'
                    : '💬 Customer message'}
                </span>
                <button
                  type="submit"
                  disabled={isSendingMessage || !noteContent.trim()}
                  className={`flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold text-white transition-all shadow-xs disabled:opacity-50 ${
                    isInternalNote
                      ? 'bg-amber-600 hover:bg-amber-700'
                      : 'bg-indigo-600 hover:bg-indigo-700'
                  }`}
                >
                  <Send className="w-3.5 h-3.5" />
                  <span>{isSendingMessage ? 'Sending...' : isInternalNote ? 'Save Note' : 'Send Reply'}</span>
                </button>
              </div>
            </form>
          </div>
        </div>

        {/* Right Column: AI Investigation, Classification & Root Cause (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          {/* Classification Insights Card */}
          {ticket.classification && (
            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-2.5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bot className="w-4 h-4 text-indigo-600" />
                  <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Classification
                  </h2>
                </div>
                <span className="text-[10px] font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded border border-indigo-200">
                  {(ticket.classification.confidence * 100).toFixed(0)}% Confidence
                </span>
              </div>

              <div>
                <p className="text-xs font-bold text-slate-900 capitalize">
                  {ticket.classification.category.replace(/_/g, ' ')}
                </p>
                <p className="text-[11px] text-slate-500 mt-1 leading-relaxed">
                  {ticket.classification.reasoning}
                </p>
              </div>
            </div>
          )}

          {/* Investigation Summary Card */}
          {ticket.investigation ? (
            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="w-4 h-4 text-indigo-600" />
                  <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Investigation
                  </h2>
                </div>
                <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
                  Complete
                </span>
              </div>

              <div className="text-xs space-y-2">
                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Root Cause Hypothesis:
                  </span>
                  <p className="text-slate-800 font-medium leading-snug mt-0.5">
                    {ticket.investigation.root_cause_hypothesis}
                  </p>
                </div>

                <div>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block">
                    Discrepancy:
                  </span>
                  <p className="text-rose-700 bg-rose-50 p-2 rounded-lg border border-rose-200 text-[11px] mt-0.5">
                    {ticket.investigation.discrepancy}
                  </p>
                </div>

                {ticket.investigation.verified_facts_json.length > 0 && (
                  <div>
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                      Verified Facts:
                    </span>
                    <ul className="space-y-1 text-[11px] text-slate-600">
                      {ticket.investigation.verified_facts_json.map((f, i) => (
                        <li key={i} className="flex items-start gap-1.5">
                          <Check className="w-3 h-3 text-emerald-600 flex-shrink-0 mt-0.5" />
                          <span>{f}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200 text-xs text-slate-500 space-y-2">
              <div className="flex items-center gap-2 text-slate-700 font-bold">
                <Activity className="w-4 h-4" />
                <span>No Investigation Yet</span>
              </div>
              <p className="text-[11px]">
                Investigation agent will automatically run when ticket transitions to Investigating.
              </p>
            </div>
          )}

          {/* Extracted Entities Card */}
          {ticket.entities.length > 0 && (
            <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-2">
              <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                Extracted Entities
              </h2>
              <div className="space-y-1.5">
                {ticket.entities.map((e) => (
                  <div
                    key={e.id}
                    className="flex items-center justify-between text-xs p-1.5 rounded-lg bg-slate-50 border border-slate-100"
                  >
                    <span className="text-[11px] text-slate-500 font-medium capitalize">
                      {e.entity_type.replace(/_/g, ' ')}:
                    </span>
                    <span className="font-mono font-bold text-indigo-900">{e.entity_value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
