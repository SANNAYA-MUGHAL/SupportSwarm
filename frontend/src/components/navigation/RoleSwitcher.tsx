'use client';

import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Shield, Check, RefreshCw } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { UserRole } from '@/types/auth';

const ROLES: { role: UserRole; title: string; badge: string; desc: string }[] = [
  {
    role: 'support_lead',
    title: 'Support Lead',
    badge: 'Approver',
    desc: 'Approves responses, manages refunds & incidents',
  },
  {
    role: 'support_agent',
    title: 'Support Agent',
    badge: 'Operator',
    desc: 'Triages tickets, reviews AI drafts & voice notes',
  },
  {
    role: 'product_manager',
    title: 'Product Manager',
    badge: 'Insights',
    desc: 'Evaluates product opportunities & recurring issues',
  },
  {
    role: 'qa_engineer',
    title: 'QA Engineer',
    badge: 'Bug Triage',
    desc: 'Reviews technical incident evidence & exports bugs',
  },
  {
    role: 'admin',
    title: 'Admin',
    badge: 'Full Access',
    desc: 'Full organization settings, AI controls & audit access',
  },
  {
    role: 'viewer',
    title: 'Executive Viewer',
    badge: 'Read-Only',
    desc: 'Observes high-level analytics & metrics',
  },
];

export function RoleSwitcher() {
  const { user, switchRole, isLoading } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const currentRoleObj = ROLES.find((r) => r.role === user?.role) || ROLES[0];

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        disabled={isLoading}
        className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-medium bg-slate-100 hover:bg-slate-200 text-slate-800 border border-slate-300 transition-colors shadow-sm"
        title="Quick Role Switcher for Demonstration"
      >
        <Shield className="w-3.5 h-3.5 text-indigo-600" />
        <span className="text-slate-500 font-normal">Persona:</span>
        <span className="font-semibold text-slate-900">{currentRoleObj.title}</span>
        {isLoading ? (
          <RefreshCw className="w-3 h-3 text-slate-400 animate-spin" />
        ) : (
          <ChevronDown className="w-3 h-3 text-slate-500" />
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-xl border border-slate-200 py-2 z-50 animate-in fade-in zoom-in-95 duration-100">
          <div className="px-3 py-1.5 border-b border-slate-100">
            <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              Demo Persona Switcher
            </p>
            <p className="text-[11px] text-slate-500">
              Test SupportSwarm with different role permissions
            </p>
          </div>

          <div className="py-1">
            {ROLES.map((r) => {
              const isSelected = user?.role === r.role;
              return (
                <button
                  key={r.role}
                  onClick={async () => {
                    setIsOpen(false);
                    await switchRole(r.role);
                  }}
                  className={`w-full text-left px-3 py-2 flex items-start gap-2.5 hover:bg-slate-50 transition-colors ${
                    isSelected ? 'bg-indigo-50/70' : ''
                  }`}
                >
                  <div className="pt-0.5">
                    {isSelected ? (
                      <Check className="w-4 h-4 text-indigo-600" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border border-slate-300" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className={`text-xs font-semibold ${isSelected ? 'text-indigo-900' : 'text-slate-800'}`}>
                        {r.title}
                      </span>
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 font-medium">
                        {r.badge}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 leading-snug mt-0.5">
                      {r.desc}
                    </p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
