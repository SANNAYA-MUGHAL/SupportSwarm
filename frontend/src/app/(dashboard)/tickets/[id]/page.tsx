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
  Bot,
  Paperclip,
  Upload,
  History,
  UserCheck,
  XCircle,
  ShieldCheck
} from 'lucide-react';
import { ApiClient } from '@/lib/api-client';
import { TicketDetailResponse, TicketStatus, AuditEventItem, MemberItem } from '@/types/ticket';
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
  const [members, setMembers] = useState<MemberItem[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditEventItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Tabs: 'conversation' | 'attachments' | 'audit'
  const [activeTab, setActiveTab] = useState<'conversation' | 'attachments' | 'audit'>('conversation');

  // Interactive feedback alerts
  const [actionAlert, setActionAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Message & Internal Note form
  const [noteContent, setNoteContent] = useState('');
  const [isInternalNote, setIsInternalNote] = useState(false);
  const [isSendingMessage, setIsSendingMessage] = useState(false);

  // State Transition & Assignment
  const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
  const [isAssigning, setIsAssigning] = useState(false);

  // Attachment upload
  const [selectedAttachment, setSelectedAttachment] = useState<File | null>(null);
  const [isUploadingAttachment, setIsUploadingAttachment] = useState(false);

  const isViewer = user?.role === 'viewer';

  const fetchTicket = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [resTicket, resMembers, resAudit] = await Promise.all([
        ApiClient.get<TicketDetailResponse>(`/tickets/${ticketId}`),
        ApiClient.get<MemberItem[]>('/organizations/members').catch(() => []),
        ApiClient.get<AuditEventItem[]>(`/tickets/${ticketId}/audit`).catch(() => [])
      ]);
      setTicket(resTicket);
      setMembers(resMembers);
      setAuditLogs(resAudit);
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
    if (isViewer) {
      setActionAlert({ type: 'error', message: 'Read-only access: Viewers cannot update ticket status.' });
      return;
    }
    setIsUpdatingStatus(true);
    setActionAlert(null);
    try {
      await ApiClient.patch(`/tickets/${ticketId}/status`, {
        target_status: targetStatus,
        reason: `Status transition by ${user?.full_name} (${user?.role})`,
      });
      setActionAlert({
        type: 'success',
        message: `Successfully transitioned ticket status to "${targetStatus.replace(/_/g, ' ')}".`
      });
      await fetchTicket();
    } catch (err: any) {
      setActionAlert({
        type: 'error',
        message: `State Machine Error: ${err.message || 'Failed to update status.'}`
      });
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleTestInvalidTransition = async () => {
    if (isViewer) {
      setActionAlert({ type: 'error', message: 'Read-only access: Viewers cannot trigger actions.' });
      return;
    }
    // Attempt an illegal transition (e.g., jump from current status to an impossible one)
    const illegalTarget = ticket?.status === 'new' ? 'resolved' : 'new';
    setIsUpdatingStatus(true);
    setActionAlert(null);
    try {
      await ApiClient.patch(`/tickets/${ticketId}/status`, {
        target_status: illegalTarget,
        reason: 'Testing invalid state transition rejection',
      });
      await fetchTicket();
    } catch (err: any) {
      setActionAlert({
        type: 'error',
        message: `State Machine Rejection Confirmed: ${err.message}`
      });
    } finally {
      setIsUpdatingStatus(false);
    }
  };

  const handleAssignUser = async (assignedUserId: string) => {
    if (isViewer) {
      setActionAlert({ type: 'error', message: 'Read-only access: Viewers cannot assign tickets.' });
      return;
    }
    setIsAssigning(true);
    setActionAlert(null);
    try {
      await ApiClient.patch(`/tickets/${ticketId}/assign`, {
        user_id: assignedUserId || null,
      });
      const assignedMember = members.find((m) => m.id === assignedUserId);
      setActionAlert({
        type: 'success',
        message: assignedUserId
          ? `Ticket assigned to ${assignedMember?.full_name || 'team member'}.`
          : 'Ticket marked as unassigned.'
      });
      await fetchTicket();
    } catch (err: any) {
      setActionAlert({
        type: 'error',
        message: `Assignment Error: ${err.message || 'Failed to assign ticket.'}`
      });
    } finally {
      setIsAssigning(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!noteContent.trim()) return;
    if (isViewer) {
      setActionAlert({ type: 'error', message: 'Read-only access: Viewers cannot send messages or notes.' });
      return;
    }

    setIsSendingMessage(true);
    setActionAlert(null);
    try {
      await ApiClient.post(`/tickets/${ticketId}/messages`, {
        content: noteContent.trim(),
        is_internal_note: isInternalNote,
        language: 'en',
      });
      setActionAlert({
        type: 'success',
        message: isInternalNote ? 'Internal note added to audit trail.' : 'Customer message sent.'
      });
      setNoteContent('');
      await fetchTicket();
    } catch (err: any) {
      setActionAlert({
        type: 'error',
        message: err.message || 'Failed to send message.'
      });
    } finally {
      setIsSendingMessage(false);
    }
  };

  const handleUploadAttachment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedAttachment) return;
    if (isViewer) {
      setActionAlert({ type: 'error', message: 'Read-only access: Viewers cannot upload attachments.' });
      return;
    }

    setIsUploadingAttachment(true);
    setActionAlert(null);
    try {
      const formData = new FormData();
      formData.append('file', selectedAttachment);

      await ApiClient.upload(`/tickets/${ticketId}/attachments`, formData);
      setActionAlert({
        type: 'success',
        message: `Attachment "${selectedAttachment.name}" uploaded successfully.`
      });
      setSelectedAttachment(null);
      await fetchTicket();
    } catch (err: any) {
      setActionAlert({
        type: 'error',
        message: `Upload Error: ${err.message || 'Failed to upload attachment.'}`
      });
    } finally {
      setIsUploadingAttachment(false);
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
              {isViewer && (
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800 border border-purple-300">
                  Viewer Mode (Read-Only)
                </span>
              )}
            </div>
            <h1 className="text-sm font-bold text-slate-900 mt-1 line-clamp-1">
              {ticket.subject}
            </h1>
          </div>
        </div>

        {/* Workflow State & Assignment Controls */}
        <div className="flex items-center gap-2.5 flex-wrap">
          {/* Reassignment Dropdown */}
          <div className="flex items-center gap-1.5">
            <UserIcon className="w-3.5 h-3.5 text-slate-500" />
            <select
              value={ticket.assigned_user_id || ''}
              disabled={isAssigning || isViewer}
              onChange={(e) => handleAssignUser(e.target.value)}
              className="text-xs font-semibold bg-white border border-slate-300 rounded-xl px-2.5 py-1.5 text-slate-900 focus:outline-none focus:border-indigo-500 shadow-xs cursor-pointer"
            >
              <option value="">Unassigned</option>
              {members.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.full_name} ({m.role.replace('_', ' ')})
                </option>
              ))}
            </select>
          </div>

          {/* Status Transition Selector */}
          <div className="flex items-center gap-1.5">
            <label className="text-xs font-medium text-slate-500">Status:</label>
            <select
              value={ticket.status}
              disabled={isUpdatingStatus || isViewer}
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

          {/* Test Invalid Transition Button for verification */}
          <button
            onClick={handleTestInvalidTransition}
            disabled={isUpdatingStatus || isViewer}
            className="text-[11px] px-2.5 py-1.5 rounded-xl border border-rose-200 text-rose-700 bg-rose-50 hover:bg-rose-100 transition-colors font-semibold"
            title="Test State Machine Rejection"
          >
            Test Invalid Jump
          </button>

          <button
            onClick={fetchTicket}
            className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition-colors shadow-xs"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-indigo-600' : ''}`} />
          </button>
        </div>
      </div>

      {/* Action Alert Banner */}
      {actionAlert && (
        <div
          className={`p-3 rounded-2xl text-xs font-medium flex items-center justify-between border ${
            actionAlert.type === 'success'
              ? 'bg-emerald-50 text-emerald-900 border-emerald-200'
              : 'bg-rose-50 text-rose-900 border-rose-200'
          }`}
        >
          <div className="flex items-center gap-2">
            {actionAlert.type === 'success' ? (
              <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
            ) : (
              <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            )}
            <span>{actionAlert.message}</span>
          </div>
          <button
            onClick={() => setActionAlert(null)}
            className="text-xs font-bold opacity-60 hover:opacity-100"
          >
            Dismiss
          </button>
        </div>
      )}

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

        {/* Middle Column: Communication Stream, Attachments & Audit Activity (6 cols) */}
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

          {/* Tab Bar: Conversation | Attachments | Audit Activity */}
          <div className="bg-white p-1 rounded-2xl border border-slate-200 shadow-xs flex items-center gap-1">
            <button
              onClick={() => setActiveTab('conversation')}
              className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                activeTab === 'conversation'
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Conversation ({ticket.messages.length})</span>
            </button>

            <button
              onClick={() => setActiveTab('attachments')}
              className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                activeTab === 'attachments'
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Paperclip className="w-3.5 h-3.5" />
              <span>Attachments ({ticket.attachments.length})</span>
            </button>

            <button
              onClick={() => setActiveTab('audit')}
              className={`flex-1 py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                activeTab === 'audit'
                  ? 'bg-indigo-600 text-white shadow-xs'
                  : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <History className="w-3.5 h-3.5" />
              <span>Audit Log ({auditLogs.length})</span>
            </button>
          </div>

          {/* TAB 1: CONVERSATION & NOTES */}
          {activeTab === 'conversation' && (
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
              <div className="space-y-3.5 max-h-[480px] overflow-y-auto pr-1">
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
              {!isViewer ? (
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
                        ? '🔒 Private note (recorded in audit log)'
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
                      <span>{isSendingMessage ? 'Saving...' : isInternalNote ? 'Save Note' : 'Send Reply'}</span>
                    </button>
                  </div>
                </form>
              ) : (
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs text-slate-500 text-center">
                  Read-only mode: Message composition is disabled for Viewer role.
                </div>
              )}
            </div>
          )}

          {/* TAB 2: ATTACHMENTS & AUDIO UPLOAD */}
          {activeTab === 'attachments' && (
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-5">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <Paperclip className="w-4 h-4 text-indigo-600" />
                  <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Attached Files & Audio Recordings
                  </h2>
                </div>
                <span className="text-[11px] text-slate-400">
                  {ticket.attachments.length} attachment(s)
                </span>
              </div>

              {/* Upload Form */}
              {!isViewer && (
                <form onSubmit={handleUploadAttachment} className="p-4 bg-slate-50 rounded-2xl border border-slate-200 space-y-3">
                  <h3 className="text-xs font-bold text-slate-900">Upload New Attachment or Audio Note</h3>
                  <div className="flex items-center gap-3">
                    <input
                      type="file"
                      id="ticket-file-input"
                      onChange={(e) => setSelectedAttachment(e.target.files?.[0] || null)}
                      className="text-xs text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer"
                    />
                    <button
                      type="submit"
                      disabled={!selectedAttachment || isUploadingAttachment}
                      className="px-4 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-semibold flex items-center gap-1.5 disabled:opacity-50 transition-all shadow-xs"
                    >
                      <Upload className="w-3.5 h-3.5" />
                      <span>{isUploadingAttachment ? 'Uploading...' : 'Upload File'}</span>
                    </button>
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Supported: MP3, WAV, M4A, OGG, PNG, JPG, PDF (max 25MB). Audio files will be transcribable by Whisper.
                  </p>
                </form>
              )}

              {/* Attachment List */}
              {ticket.attachments.length > 0 ? (
                <div className="space-y-2.5">
                  {ticket.attachments.map((att) => {
                    const isAudio = att.file_type.includes('audio') || att.file_name.endsWith('.mp3') || att.file_name.endsWith('.wav');
                    return (
                      <div
                        key={att.id}
                        className="p-3.5 rounded-2xl border border-slate-200 bg-slate-50/70 flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                      >
                        <div className="flex items-center gap-3">
                          <div className={`w-9 h-9 rounded-xl flex items-center justify-center ${isAudio ? 'bg-indigo-100 text-indigo-700' : 'bg-slate-200 text-slate-700'}`}>
                            {isAudio ? <Mic className="w-4 h-4" /> : <FileText className="w-4 h-4" />}
                          </div>
                          <div>
                            <p className="text-xs font-bold text-slate-900 line-clamp-1">{att.file_name}</p>
                            <p className="text-[10px] text-slate-500">
                              {(att.file_size / 1024).toFixed(1)} KB • {att.file_type} • {new Date(att.created_at).toLocaleDateString()}
                            </p>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          {isAudio && (
                            <audio controls src={att.storage_url} className="h-7 max-w-[200px]" />
                          )}
                          <a
                            href={att.storage_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="px-3 py-1 rounded-xl bg-white border border-slate-200 hover:bg-slate-100 text-[11px] font-semibold text-indigo-600 transition-colors shadow-xs"
                          >
                            Download
                          </a>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="p-8 text-center border border-dashed border-slate-200 rounded-2xl text-slate-400 text-xs">
                  No files or audio notes attached yet.
                </div>
              )}
            </div>
          )}

          {/* TAB 3: AUDIT ACTIVITY & TIMELINE */}
          {activeTab === 'audit' && (
            <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
              <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                <div className="flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-indigo-600" />
                  <h2 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                    Immutable Audit Trail & Status History
                  </h2>
                </div>
                <span className="text-[11px] text-slate-400">
                  {auditLogs.length} event(s) recorded
                </span>
              </div>

              {auditLogs.length > 0 ? (
                <div className="space-y-3 max-h-[520px] overflow-y-auto pr-1">
                  {auditLogs.map((log) => (
                    <div
                      key={log.id}
                      className="p-3 rounded-xl border border-slate-200 bg-slate-50/80 text-xs space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                            {log.action}
                          </span>
                          <span className="font-semibold text-slate-900 text-[11px]">
                            {log.actor_name || 'System'}
                          </span>
                          <span className="text-[10px] text-slate-400">
                            ({log.actor_type})
                          </span>
                        </div>
                        <span className="text-[10px] text-slate-400 font-mono">
                          {new Date(log.created_at).toLocaleString('en-PK')}
                        </span>
                      </div>

                      {log.old_state_json && log.new_state_json && (
                        <div className="text-[11px] font-mono text-slate-600 bg-white p-2 rounded border border-slate-200">
                          {log.old_state_json.status && log.new_state_json.status && (
                            <span className="text-slate-800">
                              Status: <span className="text-rose-600 line-through">{log.old_state_json.status}</span> → <span className="text-emerald-600 font-bold">{log.new_state_json.status}</span>
                            </span>
                          )}
                          {log.new_state_json.assigned_user_name && (
                            <span className="text-slate-800">
                              Assigned to: <span className="font-bold text-indigo-600">{log.new_state_json.assigned_user_name}</span>
                            </span>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 text-center border border-dashed border-slate-200 rounded-2xl text-slate-400 text-xs">
                  No audit entries recorded for this ticket yet.
                </div>
              )}
            </div>
          )}
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

