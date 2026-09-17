'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Inbox,
  Mic,
  CheckCircle2,
  AlertTriangle,
  Lightbulb,
  BookOpen,
  BarChart3,
  Bot,
  Sliders,
  Users,
  ShieldCheck,
  Cpu,
  Layers
} from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

interface NavItem {
  name: string;
  href: string;
  icon: React.ElementType;
  badge?: string | number;
  badgeColor?: string;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

export function Sidebar() {
  const pathname = usePathname();
  const { user, organization } = useAuth();

  const sections: NavSection[] = [
    {
      title: 'Support Operations',
      items: [
        { name: 'Command Center', href: '/', icon: LayoutDashboard },
        { name: 'Ticket Inbox', href: '/tickets', icon: Inbox, badge: '105' },
        { name: 'Voice Console', href: '/voice', icon: Mic, badge: '26' },
        {
          name: 'Approvals Queue',
          href: '/approvals',
          icon: CheckCircle2,
          badge: '14',
          badgeColor: 'bg-amber-100 text-amber-800 border border-amber-300'
        },
      ],
    },
    {
      title: 'Intelligence & Product',
      items: [
        {
          name: 'Incidents & Clusters',
          href: '/incidents',
          icon: AlertTriangle,
          badge: '2 Active',
          badgeColor: 'bg-rose-100 text-rose-800 border border-rose-300'
        },
        { name: 'Product Opportunities', href: '/product-intelligence', icon: Lightbulb, badge: '5' },
        { name: 'Knowledge Base', href: '/knowledge', icon: BookOpen },
        { name: 'Analytics & SLA', href: '/analytics', icon: BarChart3 },
      ],
    },
    {
      title: 'Agent Orchestration & Governance',
      items: [
        { name: 'Agent Activity Center', href: '/agents', icon: Bot },
        { name: 'Integrations Hub', href: '/integrations', icon: Layers },
        { name: 'Team & RBAC', href: '/team', icon: Users },
        { name: 'Audit History', href: '/settings/audit', icon: ShieldCheck },
        { name: 'AI & Safety Settings', href: '/settings/ai', icon: Cpu },
      ],
    },
  ];

  return (
    <aside className="w-64 bg-slate-900 text-slate-300 flex flex-col flex-shrink-0 h-screen border-r border-slate-800 select-none">
      {/* Brand Header */}
      <div className="h-16 flex items-center px-5 border-b border-slate-800 gap-3">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold shadow-md shadow-indigo-500/20">
          <Bot className="w-5 h-5 text-white" />
        </div>
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5">
            <span className="font-bold text-white text-base tracking-tight">SupportSwarm</span>
            <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded">
              MVP
            </span>
          </div>
          <span className="text-xs text-slate-400 truncate max-w-[140px]">
            {organization?.name || 'SwiftPay FinTech'}
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <div className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {sections.map((section) => (
          <div key={section.title} className="space-y-1">
            <h3 className="px-3 text-[11px] font-semibold uppercase tracking-wider text-slate-500">
              {section.title}
            </h3>
            <div className="space-y-0.5 pt-1">
              {section.items.map((item) => {
                const Icon = item.icon;
                const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                      isActive
                        ? 'bg-indigo-600 text-white shadow-sm'
                        : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                      <span>{item.name}</span>
                    </div>
                    {item.badge && (
                      <span
                        className={`text-[10px] px-1.5 py-0.5 rounded-full font-semibold ${
                          item.badgeColor ||
                          (isActive ? 'bg-indigo-700 text-white' : 'bg-slate-800 text-slate-400')
                        }`}
                      >
                        {item.badge}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* User Footer Card */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/40">
        <div className="flex items-center gap-3 px-2 py-1.5 rounded-lg bg-slate-800/40 border border-slate-700/50">
          <div className="w-8 h-8 rounded-full bg-slate-700 text-indigo-300 font-semibold flex items-center justify-center text-xs border border-slate-600">
            {user?.full_name ? user.full_name.charAt(0) : 'U'}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-white truncate">
              {user?.full_name || 'Guest User'}
            </p>
            <p className="text-[10px] text-indigo-400 capitalize font-medium truncate">
              {user?.role ? user.role.replace('_', ' ') : 'Viewing'}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
