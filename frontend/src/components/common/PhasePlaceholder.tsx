'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft, ArrowRight, Sparkles, CheckCircle2, Clock, Inbox, PlusCircle } from 'lucide-react';

interface PhasePlaceholderProps {
  phaseNumber: number;
  title: string;
  subtitle: string;
  description: string;
  features: string[];
  scenarioTag?: string;
  icon: React.ElementType;
}

export function PhasePlaceholder({
  phaseNumber,
  title,
  subtitle,
  description,
  features,
  scenarioTag,
  icon: Icon,
}: PhasePlaceholderProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6 py-4">
      {/* Back button */}
      <div>
        <Link
          href="/tickets"
          className="inline-flex items-center gap-2 text-xs font-semibold text-slate-500 hover:text-indigo-600 transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Ticket Inbox (Phase 2 Active)</span>
        </Link>
      </div>

      {/* Main Feature Announcement Card */}
      <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-xs overflow-hidden relative">
        <div className="absolute top-0 right-0 w-80 h-80 bg-gradient-to-bl from-indigo-50 via-slate-50 to-transparent rounded-full -mr-20 -mt-20 pointer-events-none" />

        <div className="relative z-10 space-y-5">
          <div className="flex flex-wrap items-center gap-3">
            <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-amber-50 text-amber-800 border border-amber-200 flex items-center gap-1.5">
              <Clock className="w-3.5 h-3.5" />
              Scheduled for Phase {phaseNumber}
            </span>
            {scenarioTag && (
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700 border border-indigo-200">
                {scenarioTag}
              </span>
            )}
          </div>

          <div className="flex items-start gap-4">
            <div className="w-12 h-12 rounded-2xl bg-indigo-600 text-white flex items-center justify-center flex-shrink-0 shadow-md shadow-indigo-500/20">
              <Icon className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900 tracking-tight">{title}</h1>
              <p className="text-sm text-slate-500 mt-1">{subtitle}</p>
            </div>
          </div>

          <p className="text-sm text-slate-600 leading-relaxed max-w-2xl">
            {description}
          </p>

          <div className="border-t border-slate-100 pt-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-3">
              Key Capabilities in Phase {phaseNumber}:
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {features.map((feature, idx) => (
                <div key={idx} className="flex items-start gap-2.5 p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs text-slate-700">
                  <CheckCircle2 className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                  <span>{feature}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Action CTA to current testable Phase 2 */}
          <div className="pt-4 flex flex-wrap items-center gap-3">
            <Link
              href="/tickets"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-sm"
            >
              <Inbox className="w-4 h-4" />
              <span>Test Omnichannel Inbox (Phase 2)</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
            <Link
              href="/tickets/new"
              className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
            >
              <PlusCircle className="w-4 h-4" />
              <span>Submit / Ingest New Ticket</span>
            </Link>
          </div>
        </div>
      </div>

      {/* Phase Roadmap Status Card */}
      <div className="bg-slate-900 text-slate-200 rounded-2xl p-6 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-indigo-400" />
            <h2 className="text-sm font-bold text-white">SupportSwarm Development Roadmap</h2>
          </div>
          <span className="text-xs text-indigo-400 font-medium">Currently in Phase 2 Gate Review</span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30">
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold mb-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Phase 1</span>
            </div>
            <p className="text-[11px] text-slate-300">Foundation & Auth (Complete)</p>
          </div>

          <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-500/30">
            <div className="flex items-center gap-1.5 text-emerald-400 font-bold mb-1">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>Phase 2</span>
            </div>
            <p className="text-[11px] text-slate-300">Ticket Operations (Complete & Ready)</p>
          </div>

          <div className={`p-3 rounded-xl ${phaseNumber === 3 ? 'bg-indigo-950/60 border border-indigo-500/50 text-white' : 'bg-slate-800/40 border border-slate-700/50 text-slate-400'}`}>
            <span className="font-bold block mb-1">Phase 3</span>
            <p className="text-[11px]">Voice & AI Triage (Next)</p>
          </div>

          <div className={`p-3 rounded-xl ${phaseNumber >= 4 ? 'bg-indigo-950/60 border border-indigo-500/50 text-white' : 'bg-slate-800/40 border border-slate-700/50 text-slate-400'}`}>
            <span className="font-bold block mb-1">Phases 4–8</span>
            <p className="text-[11px]">Investigation, Incidents & Insights</p>
          </div>
        </div>
      </div>
    </div>
  );
}
