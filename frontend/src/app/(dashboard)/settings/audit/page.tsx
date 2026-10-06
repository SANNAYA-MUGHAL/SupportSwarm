'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import {
  ShieldCheck,
  RefreshCw,
  Search,
  Filter,
  ArrowLeft,
  Clock,
  User as UserIcon,
  Tag,
  AlertCircle
} from 'lucide-react';
import { ApiClient } from '@/lib/api-client';
import { AuditEventItem } from '@/types/ticket';
import { useAuth } from '@/lib/auth-context';

export default function AuditLogsPage() {
  const { user } = useAuth();
  const [logs, setLogs] = useState<AuditEventItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [actionFilter, setActionFilter] = useState('all');

  const fetchAuditLogs = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await ApiClient.get<AuditEventItem[]>('/audit/logs?limit=100');
      setLogs(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch audit logs.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAuditLogs();
  }, [fetchAuditLogs]);

  const filteredLogs = logs.filter((log) => {
    const matchesAction = actionFilter === 'all' || log.action.includes(actionFilter);
    const matchesSearch =
      !search ||
      log.action.toLowerCase().includes(search.toLowerCase()) ||
      (log.actor_name && log.actor_name.toLowerCase().includes(search.toLowerCase())) ||
      (log.entity_id && log.entity_id.toLowerCase().includes(search.toLowerCase()));
    return matchesAction && matchesSearch;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-indigo-50 border border-indigo-200 flex items-center justify-center text-indigo-600">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <h1 className="text-base font-bold text-slate-900">Organization Audit Trail</h1>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-50 text-emerald-700 border border-emerald-200">
              Immutable
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-1">
            Cryptographically sealed and traceable ledger of every ticket creation, status transition, assignment, message, and administrative event.
          </p>
        </div>

        <button
          onClick={fetchAuditLogs}
          disabled={isLoading}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold bg-white border border-slate-200 text-slate-700 hover:bg-slate-50 shadow-xs transition-colors"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-indigo-600' : ''}`} />
          <span>Refresh Ledger</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by action, actor name, or entity ID..."
            className="w-full text-xs pl-9 pr-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:border-indigo-500 text-slate-900"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-400" />
          <select
            value={actionFilter}
            onChange={(e) => setActionFilter(e.target.value)}
            className="text-xs bg-white border border-slate-200 rounded-xl px-3 py-2 text-slate-700 focus:outline-none focus:border-indigo-500 cursor-pointer"
          >
            <option value="all">All Actions</option>
            <option value="ticket.created">Ticket Created</option>
            <option value="ticket.assigned">Ticket Assigned</option>
            <option value="ticket.status_change">Status Change</option>
            <option value="ticket.note_added">Internal Note</option>
            <option value="ticket.message_sent">Message Sent</option>
            <option value="ticket.attachment_added">Attachment Added</option>
            <option value="organization">Organization Setup</option>
          </select>
        </div>
      </div>

      {/* Audit Log Table */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-xs overflow-hidden">
        {isLoading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading audit log entries...</div>
        ) : error ? (
          <div className="p-8 text-center text-xs text-rose-600 flex flex-col items-center gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>{error}</span>
          </div>
        ) : filteredLogs.length === 0 ? (
          <div className="p-12 text-center text-xs text-slate-400">No audit log records found matching the filter.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-100 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                <tr>
                  <th className="py-3 px-4">Timestamp (PKT)</th>
                  <th className="py-3 px-4">Action</th>
                  <th className="py-3 px-4">Actor</th>
                  <th className="py-3 px-4">Entity</th>
                  <th className="py-3 px-4">State Transition / Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-50/70 transition-colors">
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-500 whitespace-nowrap">
                      {new Date(log.created_at).toLocaleString('en-PK')}
                    </td>
                    <td className="py-3 px-4">
                      <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-indigo-50 text-indigo-700 border border-indigo-200">
                        {log.action}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-semibold text-slate-900">{log.actor_name || 'System'}</div>
                      <div className="text-[10px] text-slate-400 capitalize">{log.actor_type}</div>
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-600">
                      {log.entity_type}:{log.entity_id ? log.entity_id.slice(0, 8) + '...' : '-'}
                    </td>
                    <td className="py-3 px-4 font-mono text-[11px] text-slate-700 max-w-xs truncate">
                      {log.old_state_json?.status && log.new_state_json?.status ? (
                        <span>
                          <span className="text-rose-600 line-through">{log.old_state_json.status}</span> → <span className="text-emerald-600 font-bold">{log.new_state_json.status}</span>
                        </span>
                      ) : log.new_state_json?.assigned_user_name ? (
                        <span>Assigned to: <strong className="text-indigo-600">{log.new_state_json.assigned_user_name}</strong></span>
                      ) : log.new_state_json?.ticket_number ? (
                        <span>Ticket: {log.new_state_json.ticket_number}</span>
                      ) : (
                        JSON.stringify(log.new_state_json || {})
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
