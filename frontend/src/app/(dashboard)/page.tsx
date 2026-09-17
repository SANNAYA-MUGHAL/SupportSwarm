'use client';

import React from 'react';
import Link from 'next/link';
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Inbox,
  TrendingUp,
  Sparkles,
  ArrowUpRight,
  ShieldAlert,
  Bot,
  Lightbulb,
  ExternalLink,
  ChevronRight,
  Activity
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

export default function DashboardPage() {
  const { user, organization } = useAuth();

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Welcome & Context Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Support Operations Command Center
            </h1>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
              Live Monitoring
            </span>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Real-time multi-agent triage, technical investigation, and product intelligence for {organization?.name || 'SwiftPay FinTech'}.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/approvals"
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-sm"
          >
            <CheckCircle2 className="w-4 h-4" />
            <span>Review Approvals (14)</span>
          </Link>
          <Link
            href="/tickets"
            className="flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
          >
            <Inbox className="w-4 h-4" />
            <span>View All Tickets</span>
          </Link>
        </div>
      </div>

      {/* Critical Incident Alert Banner (Scenario A Active Incident) */}
      <div className="bg-rose-50 border border-rose-200 rounded-2xl p-4 shadow-xs">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-start gap-3">
            <div className="w-9 h-9 rounded-xl bg-rose-600 text-white flex items-center justify-center flex-shrink-0 shadow-sm shadow-rose-500/30">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 bg-rose-200 text-rose-900 rounded">
                  Active S1 Incident
                </span>
                <span className="text-xs font-semibold text-rose-950">INC-101: Payment Captured but Order Creation RPC Failure</span>
              </div>
              <p className="text-xs text-rose-800 mt-1">
                5 customers reported payments captured via JazzCash/EasyPaisa with missing orders within 30 minutes. Spike velocity: 6.5x above baseline.
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 sm:self-center self-end">
            <Link
              href="/incidents"
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-white text-rose-700 hover:bg-rose-100 border border-rose-300 transition-colors shadow-xs"
            >
              <span>Inspect Incident & Bug</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Key Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Metric 1 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium">Critical Tickets</span>
            <AlertTriangle className="w-4 h-4 text-rose-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">8</span>
            <span className="text-[11px] font-semibold text-rose-600 bg-rose-50 px-1.5 py-0.5 rounded">
              3 SLA At Risk
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Requires technical investigation & action
          </p>
        </div>

        {/* Metric 2 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium">Pending Approvals</span>
            <CheckCircle2 className="w-4 h-4 text-amber-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">14</span>
            <span className="text-[11px] font-semibold text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded">
              Human Gate
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            10 response drafts, 3 refunds, 1 incident
          </p>
        </div>

        {/* Metric 3 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium">Avg Resolution Time</span>
            <Clock className="w-4 h-4 text-indigo-500" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">42m</span>
            <span className="text-[11px] font-semibold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded flex items-center">
              <TrendingUp className="w-3 h-3 mr-0.5" /> -68%
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Down from 135m manual baseline
          </p>
        </div>

        {/* Metric 4 */}
        <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-xs">
          <div className="flex items-center justify-between text-slate-500 mb-2">
            <span className="text-xs font-medium">AI Support Hours Saved</span>
            <Sparkles className="w-4 h-4 text-indigo-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900">142h</span>
            <span className="text-[11px] font-semibold text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">
              This Week
            </span>
          </div>
          <p className="text-[11px] text-slate-400 mt-2">
            Through automated query & investigations
          </p>
        </div>
      </div>

      {/* Main Grid: Operational Queue & Intelligence Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Urgent Ticket Queue (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Inbox className="w-4 h-4 text-indigo-600" />
                <h2 className="text-sm font-bold text-slate-900">Urgent Tickets Requiring Action</h2>
              </div>
              <Link
                href="/tickets"
                className="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
              >
                <span>View Inbox (105)</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="divide-y divide-slate-100">
              {/* Ticket Row 1 */}
              <div className="py-3 flex items-start justify-between gap-3 hover:bg-slate-50/50 p-2 rounded-xl transition-colors">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-[11px] font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded">
                      TCK-10000
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-rose-100 text-rose-800">
                      S1 Critical
                    </span>
                    <span className="text-[11px] text-slate-400">• Web Chat</span>
                  </div>
                  <h3 className="text-xs font-semibold text-slate-900 truncate">
                    Payment Deducted but Order Not Created (PKR 4,500)
                  </h3>
                  <p className="text-[11px] text-slate-500 truncate mt-0.5">
                    Customer: Ali Raza (VIP) • Investigation: Captured on JazzCash; order RPC timed out.
                  </p>
                </div>
                <Link
                  href="/tickets"
                  className="px-2.5 py-1 text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg flex-shrink-0 transition-colors"
                >
                  Inspect
                </Link>
              </div>

              {/* Ticket Row 2 */}
              <div className="py-3 flex items-start justify-between gap-3 hover:bg-slate-50/50 p-2 rounded-xl transition-colors">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-[11px] font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded">
                      TCK-10001
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-100 text-amber-800">
                      S2 High
                    </span>
                    <span className="text-[11px] text-slate-400">• Voice Note (Urdu)</span>
                  </div>
                  <h3 className="text-xs font-semibold text-slate-900 truncate">
                    Refund delay: &quot;Mera payment kat chuka hai JazzCash se...&quot;
                  </h3>
                  <p className="text-[11px] text-slate-500 truncate mt-0.5">
                    Customer: Fatima Noor • Whisper transcribed with 96% confidence score.
                  </p>
                </div>
                <Link
                  href="/voice"
                  className="px-2.5 py-1 text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg flex-shrink-0 transition-colors"
                >
                  Listen
                </Link>
              </div>

              {/* Ticket Row 3 */}
              <div className="py-3 flex items-start justify-between gap-3 hover:bg-slate-50/50 p-2 rounded-xl transition-colors">
                <div className="min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-mono text-[11px] font-bold text-indigo-700 bg-indigo-50 px-1.5 py-0.5 rounded">
                      TCK-10005
                    </span>
                    <span className="px-1.5 py-0.5 rounded text-[10px] font-semibold bg-amber-100 text-amber-800">
                      S2 High
                    </span>
                    <span className="text-[11px] text-slate-400">• SMS OTP</span>
                  </div>
                  <h3 className="text-xs font-semibold text-slate-900 truncate">
                    Did Not Receive Verification SMS for Login
                  </h3>
                  <p className="text-[11px] text-slate-500 truncate mt-0.5">
                    Customer: Bilal Mansoor • Region: Punjab (Correlated with INC-102 gateway latency).
                  </p>
                </div>
                <Link
                  href="/tickets"
                  className="px-2.5 py-1 text-xs font-medium text-indigo-600 bg-indigo-50 hover:bg-indigo-100 rounded-lg flex-shrink-0 transition-colors"
                >
                  Inspect
                </Link>
              </div>
            </div>
          </div>

          {/* Agent Activity Live Telemetry */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Bot className="w-4 h-4 text-indigo-600" />
                <h2 className="text-sm font-bold text-slate-900">Live Agent Pipeline Telemetry</h2>
              </div>
              <Link
                href="/agents"
                className="text-xs font-medium text-indigo-600 hover:text-indigo-800 flex items-center gap-1"
              >
                <span>Activity Center</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </Link>
            </div>

            <div className="space-y-3">
              {[
                {
                  agent: 'Support Director Agent',
                  action: 'Orchestrated investigation workflow for TCK-10000; dispatched to Approval Queue',
                  time: '12s ago',
                  status: 'completed',
                },
                {
                  agent: 'Investigation Agent',
                  action: 'Queried Mock Payment & Order APIs; identified RPC timeout discrepancy on TXN-88921',
                  time: '45s ago',
                  status: 'completed',
                },
                {
                  agent: 'Incident Detection Agent',
                  action: 'Correlated 5 payment pending tickets in 30 mins; generated INC-101 incident suggestion',
                  time: '2m ago',
                  status: 'flagged',
                },
                {
                  agent: 'Intake Agent + Whisper',
                  action: 'Transcribed 14.5s Urdu voice note; extracted entities [ORD-20001, PKR 4,500]',
                  time: '4m ago',
                  status: 'completed',
                },
              ].map((log, i) => (
                <div key={i} className="flex items-start gap-3 text-xs p-2.5 rounded-xl bg-slate-50 border border-slate-100">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 mt-1.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-0.5">
                      <span className="font-semibold text-slate-800">{log.agent}</span>
                      <span className="text-[10px] text-slate-400">{log.time}</span>
                    </div>
                    <p className="text-slate-600 text-[11px] leading-relaxed">{log.action}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Emerging Intelligence & Opportunities (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          {/* Product Opportunity Card */}
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Lightbulb className="w-4 h-4 text-amber-500" />
                <h2 className="text-sm font-bold text-slate-900">Prioritized Product Opportunity</h2>
              </div>
              <span className="text-[10px] font-semibold px-2 py-0.5 bg-amber-50 text-amber-800 border border-amber-200 rounded-full">
                High Impact
              </span>
            </div>

            <h3 className="text-xs font-bold text-slate-900">
              Automated Instant Reconciliation for Captures Without Orders
            </h3>
            <p className="text-[11px] text-slate-600 mt-1 leading-relaxed">
              Derived from 48 recurring complaints affecting 182 users. Estimated lost revenue or delayed settlements: PKR 850,000.
            </p>

            <div className="mt-3 p-3 bg-slate-50 rounded-xl border border-slate-200/70 text-[11px] space-y-1.5">
              <div className="flex justify-between">
                <span className="text-slate-500">Pattern:</span>
                <span className="font-medium text-slate-800">Captured payment, failed order RPC</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Proposed Solution:</span>
                <span className="font-medium text-slate-800">Async webhook auto-retry worker</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Status:</span>
                <span className="font-semibold text-indigo-600 capitalize">Move to Discovery</span>
              </div>
            </div>

            <div className="mt-4">
              <Link
                href="/product-intelligence"
                className="w-full inline-flex items-center justify-center gap-1.5 py-2 px-3 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
              >
                <span>Explore All 5 Opportunities</span>
                <ArrowUpRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>

          {/* Quick Scenario Demonstration Guide Card */}
          <div className="bg-indigo-50/60 p-5 rounded-2xl border border-indigo-100">
            <div className="flex items-center gap-2 mb-2">
              <Activity className="w-4 h-4 text-indigo-700" />
              <h2 className="text-xs font-bold text-indigo-950 uppercase tracking-wide">
                Evaluation Scenarios
              </h2>
            </div>
            <p className="text-xs text-indigo-900 leading-relaxed mb-3">
              The environment is pre-seeded with four end-to-end scenarios ready for demonstration:
            </p>
            <div className="space-y-2 text-[11px]">
              <div className="p-2 bg-white/80 rounded-lg border border-indigo-100">
                <span className="font-bold text-indigo-900">Scenario A:</span> 5 payment captured complaints trigger S1 incident INC-101 and engineering bug report.
              </div>
              <div className="p-2 bg-white/80 rounded-lg border border-indigo-100">
                <span className="font-bold text-indigo-900">Scenario B:</span> Refund delay distinguishes merchant vs bank clearing without unsupported promises.
              </div>
              <div className="p-2 bg-white/80 rounded-lg border border-indigo-100">
                <span className="font-bold text-indigo-900">Scenario C:</span> Regional SMS OTP failure grouped by region and linked to SMS gateway health.
              </div>
              <div className="p-2 bg-white/80 rounded-lg border border-indigo-100">
                <span className="font-bold text-indigo-900">Scenario D:</span> Discount code confusion converted into UX checkout opportunity instead of a bug.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
