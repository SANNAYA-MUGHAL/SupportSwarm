'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

import { Bot, Shield, ArrowRight, Sparkles, CheckCircle2, Lock } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';
import { UserRole } from '@/types/auth';

const DEMO_ACCOUNTS: { role: UserRole; name: string; title: string; desc: string; badge: string }[] = [
  {
    role: 'support_lead',
    name: 'Hamza Tariq',
    title: 'Support Lead',
    desc: 'Approves customer responses, reviews refunds, declares incidents',
    badge: 'Recommended Demo',
  },
  {
    role: 'support_agent',
    name: 'Bilal Ahmed',
    title: 'Support Agent',
    desc: 'Triages omnichannel inbox, inspects investigation timelines',
    badge: 'Operations',
  },
  {
    role: 'product_manager',
    name: 'Omar Farooq',
    title: 'Product Manager',
    desc: 'Explores product opportunities, pain point clusters & experiments',
    badge: 'Product Strategy',
  },
  {
    role: 'qa_engineer',
    name: 'Zainab Malik',
    title: 'QA Engineer',
    desc: 'Generates engineering bug reports with reproduction steps & logs',
    badge: 'Engineering',
  },
  {
    role: 'admin',
    name: 'Sarah Khan',
    title: 'Platform Admin',
    desc: 'Configures AI budgets, prompts, team permissions & audit logs',
    badge: 'Full Access',
  },
  {
    role: 'viewer',
    name: 'Amina Hassan',
    title: 'Executive Viewer',
    desc: 'High-level business telemetry, SLA compliance & cost tracking',
    badge: 'Executive',
  },
];

export default function LoginPage() {
  const router = useRouter();
  const { login, demoLogin, isLoading } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loadingRole, setLoadingRole] = useState<string | null>(null);

  useEffect(() => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const auto = params.get('auto') as UserRole | null;
      if (auto && DEMO_ACCOUNTS.some((a) => a.role === auto)) {
        demoLogin(auto).then(() => {
          const redirect = params.get('redirect') || '/tickets';
          router.push(redirect);
        });
      }
    }
  }, [demoLogin, router]);


  const handleStandardLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      await login(email, password);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    }
  };

  const handleDemoLogin = async (role: UserRole) => {
    setError(null);
    setLoadingRole(role);
    try {
      await demoLogin(role);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Demo login failed.');
    } finally {
      setLoadingRole(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex items-center justify-center w-12 h-12 rounded-xl bg-indigo-600 text-white shadow-lg shadow-indigo-500/30 mb-4">
          <Bot className="w-7 h-7" />
        </div>
        <h2 className="text-2xl font-bold tracking-tight text-slate-900">
          SupportSwarm
        </h2>
        <p className="mt-1 text-xs text-slate-500">
          AI Customer Support & Product Intelligence Platform
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-4xl px-4">
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
          {/* Left Column: 1-Click Demo Login */}
          <div className="md:col-span-7 bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-indigo-600" />
                <h3 className="text-sm font-bold text-slate-900">Instant Demo Login</h3>
              </div>
              <span className="text-[11px] font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                Seeded Environment Ready
              </span>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Select an enterprise persona to immediately enter SupportSwarm with realistic permissions and pre-seeded operational data:
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {DEMO_ACCOUNTS.map((acc) => {
                const isThisLoading = loadingRole === acc.role;
                const isRec = acc.role === 'support_lead';
                return (
                  <button
                    key={acc.role}
                    onClick={() => handleDemoLogin(acc.role)}
                    disabled={isLoading}
                    className={`text-left p-3 rounded-xl border transition-all relative ${
                      isRec
                        ? 'border-indigo-400 bg-indigo-50/40 hover:bg-indigo-50 hover:border-indigo-500 shadow-xs'
                        : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs font-bold text-slate-900">{acc.title}</span>
                      <span
                        className={`text-[9px] px-1.5 py-0.5 rounded font-semibold ${
                          isRec
                            ? 'bg-indigo-600 text-white'
                            : 'bg-slate-100 text-slate-600'
                        }`}
                      >
                        {acc.badge}
                      </span>
                    </div>
                    <p className="text-[11px] font-medium text-indigo-950 mb-1">{acc.name}</p>
                    <p className="text-[10px] text-slate-500 leading-tight line-clamp-2">
                      {acc.desc}
                    </p>
                    {isThisLoading && (
                      <div className="absolute inset-0 bg-white/80 backdrop-blur-xs rounded-xl flex items-center justify-center">
                        <div className="w-4 h-4 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Right Column: Standard Credentials Login */}
          <div className="md:col-span-5 bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-2 mb-4">
                <Lock className="w-4 h-4 text-slate-700" />
                <h3 className="text-sm font-bold text-slate-900">Account Credentials</h3>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-lg">
                  {error}
                </div>
              )}

              <form onSubmit={handleStandardLogin} className="space-y-4">
                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">
                    Work Email
                  </label>
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    className="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-700 mb-1">
                    Password
                  </label>
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full text-xs px-3 py-2 rounded-lg border border-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full flex items-center justify-center gap-2 py-2 px-4 rounded-lg text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-sm"
                >
                  <span>Sign In</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>

            <div className="mt-6 pt-4 border-t border-slate-100 text-center">
              <p className="text-[11px] text-slate-400">
                Organization not yet registered?{' '}
                <a href="/org-setup" className="text-indigo-600 hover:underline font-medium">
                  Setup New Organization
                </a>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
