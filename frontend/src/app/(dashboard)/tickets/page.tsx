'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  Search,
  Plus,
  Filter,
  RefreshCw,
  AlertCircle,
  Inbox,
  ChevronLeft,
  ChevronRight,
  Mic,
  Clock,
  User as UserIcon,
  X
} from 'lucide-react';
import { ApiClient } from '@/lib/api-client';
import { TicketListResponse, TicketListItem } from '@/types/ticket';
import { TicketStatusBadge } from '@/components/tickets/TicketStatusBadge';
import { SeverityBadge } from '@/components/tickets/SeverityBadge';
import { ChannelBadge } from '@/components/tickets/ChannelBadge';
import { useAuth } from '@/lib/auth-context';

const STATUS_TABS = [
  { key: 'all', label: 'All Tickets' },
  { key: 'new', label: 'New' },
  { key: 'triaged', label: 'Triaged' },
  { key: 'investigating', label: 'Investigating' },
  { key: 'waiting_for_approval', label: 'Waiting for Approval' },
  { key: 'waiting_for_customer', label: 'Waiting for Customer' },
  { key: 'waiting_for_internal_team', label: 'Waiting for Team' },
  { key: 'resolved', label: 'Resolved' },
  { key: 'closed', label: 'Closed' },
];

export default function TicketInboxPage() {
  const { user } = useAuth();
  const [data, setData] = useState<TicketListResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Filters State
  const [currentTab, setCurrentTab] = useState<string>('all');
  const [channel, setChannel] = useState<string>('all');
  const [severity, setSeverity] = useState<string>('all');
  const [category, setCategory] = useState<string>('all');
  const [assignee, setAssignee] = useState<string>('all');
  const [search, setSearch] = useState<string>('');
  const [page, setPage] = useState<number>(1);
  const limit = 15;

  const fetchTickets = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (currentTab !== 'all') params.append('status', currentTab);
      if (channel !== 'all') params.append('channel', channel);
      if (severity !== 'all') params.append('severity', severity);
      if (category !== 'all') params.append('category', category);
      if (assignee === 'me' && user?.id) {
        params.append('assignee', user.id);
      } else if (assignee !== 'all') {
        params.append('assignee', assignee);
      }
      if (search.trim()) params.append('search', search.trim());
      params.append('page', page.toString());
      params.append('limit', limit.toString());

      const res = await ApiClient.get<TicketListResponse>(`/tickets?${params.toString()}`);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Failed to load tickets from server');
    } finally {
      setIsLoading(false);
    }
  }, [currentTab, channel, severity, category, assignee, search, page, user?.id]);

  useEffect(() => {
    fetchTickets();
  }, [fetchTickets]);

  const handleResetFilters = () => {
    setCurrentTab('all');
    setChannel('all');
    setSeverity('all');
    setCategory('all');
    setAssignee('all');
    setSearch('');
    setPage(1);
  };

  const hasActiveFilters =
    channel !== 'all' ||
    severity !== 'all' ||
    category !== 'all' ||
    assignee !== 'all' ||
    search.trim() !== '';

  return (
    <div className="space-y-5 max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Omnichannel Ticket Inbox
            </h1>
            <span className="px-2 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
              {data ? `${data.total} Total` : '...'}
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time incoming customer complaints across Web Chat, Voice Notes, Email, and Forms.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => fetchTickets()}
            disabled={isLoading}
            className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition-colors shadow-xs"
            title="Refresh tickets"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin text-indigo-600' : ''}`} />
          </button>

          <Link
            href="/tickets/new"
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-sm"
          >
            <Plus className="w-4 h-4" />
            <span>Create New Ticket</span>
          </Link>
        </div>
      </div>

      {/* Status Tabs Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 p-1.5 shadow-xs overflow-x-auto">
        <div className="flex items-center gap-1 min-w-max">
          {STATUS_TABS.map((tab) => {
            const isActive = currentTab === tab.key;
            const count = data?.status_counts ? data.status_counts[tab.key] ?? 0 : null;
            return (
              <button
                key={tab.key}
                onClick={() => {
                  setCurrentTab(tab.key);
                  setPage(1);
                }}
                className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-xs'
                    : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/70'
                }`}
              >
                <span>{tab.label}</span>
                {count !== null && (
                  <span
                    className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                      isActive
                        ? 'bg-indigo-700 text-white'
                        : 'bg-slate-100 text-slate-600'
                    }`}
                  >
                    {count}
                  </span>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Filter and Search Controls */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-3">
        <div className="flex flex-col md:flex-row items-center gap-3">
          {/* Search Box */}
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search by ticket # (TCK-10001), subject, or customer name/email..."
              className="w-full bg-slate-50 hover:bg-slate-100/60 focus:bg-white text-xs text-slate-900 pl-9 pr-8 py-2 rounded-xl border border-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all placeholder:text-slate-400"
            />
            {search && (
              <button
                onClick={() => setSearch('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>

          {/* Filters Row */}
          <div className="flex items-center gap-2 w-full md:w-auto overflow-x-auto pb-1 md:pb-0">
            {/* Channel Filter */}
            <select
              value={channel}
              onChange={(e) => {
                setChannel(e.target.value);
                setPage(1);
              }}
              className="text-xs bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-2 font-medium text-slate-700 focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Channels</option>
              <option value="web_chat">Web Chat</option>
              <option value="voice_note">Voice Note</option>
              <option value="email">Email</option>
              <option value="support_form">Support Form</option>
            </select>

            {/* Severity Filter */}
            <select
              value={severity}
              onChange={(e) => {
                setSeverity(e.target.value);
                setPage(1);
              }}
              className="text-xs bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-2 font-medium text-slate-700 focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Severities</option>
              <option value="S1">S1 Critical</option>
              <option value="S2">S2 High</option>
              <option value="S3">S3 Medium</option>
              <option value="S4">S4 Low</option>
            </select>

            {/* Category Filter */}
            <select
              value={category}
              onChange={(e) => {
                setCategory(e.target.value);
                setPage(1);
              }}
              className="text-xs bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-2 font-medium text-slate-700 focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Categories</option>
              <option value="payment_pending">Payment Pending</option>
              <option value="duplicate_payment">Duplicate Payment</option>
              <option value="refund_delay">Refund Delay</option>
              <option value="login_otp">Login OTP</option>
              <option value="discount_code">Discount Code</option>
              <option value="order_cancellation">Order Cancellation</option>
              <option value="delivery_delay">Delivery Delay</option>
            </select>

            {/* Assignee Filter */}
            <select
              value={assignee}
              onChange={(e) => {
                setAssignee(e.target.value);
                setPage(1);
              }}
              className="text-xs bg-slate-50 border border-slate-200 rounded-xl px-2.5 py-2 font-medium text-slate-700 focus:outline-none focus:border-indigo-500"
            >
              <option value="all">All Assignees</option>
              <option value="me">Assigned to Me</option>
              <option value="unassigned">Unassigned</option>
            </select>

            {hasActiveFilters && (
              <button
                onClick={handleResetFilters}
                className="flex items-center gap-1 text-xs text-rose-600 hover:text-rose-700 font-semibold px-2 py-2 whitespace-nowrap"
              >
                <X className="w-3.5 h-3.5" />
                <span>Reset</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600" />
            <span>{error}</span>
          </div>
          <button
            onClick={fetchTickets}
            className="text-xs font-semibold underline hover:text-rose-900"
          >
            Retry
          </button>
        </div>
      )}

      {/* Tickets Data Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center space-y-3">
            <div className="w-8 h-8 border-3 border-indigo-600 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs font-medium text-slate-500">Loading omnichannel ticket inbox...</p>
          </div>
        ) : !data || data.items.length === 0 ? (
          <div className="p-16 text-center space-y-3">
            <div className="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto text-slate-400">
              <Inbox className="w-6 h-6" />
            </div>
            <h3 className="text-sm font-bold text-slate-900">No Tickets Found</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No tickets match your selected filters or search query. Try changing tabs or resetting your filters.
            </p>
            {hasActiveFilters && (
              <button
                onClick={handleResetFilters}
                className="mt-2 inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold text-indigo-600 bg-indigo-50 hover:bg-indigo-100 transition-colors"
              >
                Reset All Filters
              </button>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/70 text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-4">Ticket</th>
                  <th className="py-3 px-4">Customer</th>
                  <th className="py-3 px-4">Subject & Details</th>
                  <th className="py-3 px-3">Channel</th>
                  <th className="py-3 px-3">Severity</th>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-3">Assignee</th>
                  <th className="py-3 px-4 text-right">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
                {data.items.map((t) => (
                  <tr
                    key={t.id}
                    className="hover:bg-slate-50/80 transition-colors group cursor-pointer"
                  >
                    {/* Ticket Number */}
                    <td className="py-3.5 px-4 font-mono font-bold text-indigo-600 whitespace-nowrap">
                      <Link
                        href={`/tickets/${t.id}`}
                        className="hover:underline flex items-center gap-1.5"
                      >
                        <span>{t.ticket_number}</span>
                        {t.has_voice && (
                          <span title="Voice Note Transcript Available">
                            <Mic className="w-3 h-3 text-indigo-500" />
                          </span>
                        )}
                      </Link>
                    </td>

                    {/* Customer */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <div className="font-semibold text-slate-900">{t.customer_name}</div>
                      <div className="text-[11px] text-slate-400 flex items-center gap-1">
                        <span>{t.customer_email}</span>
                        {t.customer_segment === 'vip' && (
                          <span className="px-1 rounded bg-amber-50 text-amber-700 font-bold text-[9px] border border-amber-200">
                            VIP
                          </span>
                        )}
                      </div>
                    </td>

                    {/* Subject */}
                    <td className="py-3.5 px-4 max-w-xs sm:max-w-sm">
                      <Link
                        href={`/tickets/${t.id}`}
                        className="font-medium text-slate-800 hover:text-indigo-600 truncate block"
                      >
                        {t.subject}
                      </Link>
                      <div className="text-[11px] text-slate-400 truncate mt-0.5">
                        Category: <span className="capitalize">{t.category?.replace(/_/g, ' ') || 'General'}</span>
                      </div>
                    </td>

                    {/* Channel */}
                    <td className="py-3.5 px-3 whitespace-nowrap">
                      <ChannelBadge channel={t.channel} />
                    </td>

                    {/* Severity */}
                    <td className="py-3.5 px-3 whitespace-nowrap">
                      <SeverityBadge severity={t.severity} />
                    </td>

                    {/* Status */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <TicketStatusBadge status={t.status} />
                    </td>

                    {/* Assignee */}
                    <td className="py-3.5 px-3 whitespace-nowrap">
                      {t.assigned_user_name ? (
                        <div className="flex items-center gap-1.5 text-slate-800 font-medium">
                          <div className="w-5 h-5 rounded-full bg-slate-200 text-slate-600 flex items-center justify-center text-[10px] font-bold">
                            {t.assigned_user_name.charAt(0)}
                          </div>
                          <span className="truncate max-w-[100px]">{t.assigned_user_name}</span>
                        </div>
                      ) : (
                        <span className="text-slate-400 text-[11px] italic">Unassigned</span>
                      )}
                    </td>

                    {/* Created */}
                    <td className="py-3.5 px-4 text-right text-slate-400 text-[11px] whitespace-nowrap">
                      {new Date(t.created_at).toLocaleDateString('en-PK', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Footer */}
        {data && data.total > 0 && (
          <div className="py-3 px-4 border-t border-slate-200 bg-slate-50/50 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-600">
            <div>
              Showing <span className="font-semibold">{data.items.length}</span> of{' '}
              <span className="font-semibold">{data.total}</span> tickets
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page <= 1 || isLoading}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <span className="px-2 font-medium">
                Page {page} of {data.pages}
              </span>

              <button
                onClick={() => setPage((p) => Math.min(data.pages, p + 1))}
                disabled={page >= data.pages || isLoading}
                className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-100 disabled:opacity-40 disabled:cursor-not-allowed"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
