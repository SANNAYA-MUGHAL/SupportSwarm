'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  MessageSquare,
  FileText,
  Mail,
  Mic,
  Upload,
  CheckCircle2,
  AlertCircle,
  Sparkles
} from 'lucide-react';
import { ApiClient } from '@/lib/api-client';
import { TicketDetailResponse } from '@/types/ticket';

type IngestionMode = 'manual' | 'form' | 'email' | 'voice';

export default function NewTicketPage() {
  const router = useRouter();
  const [mode, setMode] = useState<IngestionMode>('manual');

  // Form Fields
  const [customerName, setCustomerName] = useState('Kamran Tariq');
  const [customerEmail, setCustomerEmail] = useState('kamran.tariq@gmail.com');
  const [customerPhone, setCustomerPhone] = useState('+923001234567');
  const [subject, setSubject] = useState('Payment deducted via JazzCash but order still missing');
  const [description, setDescription] = useState(
    'I made a payment of PKR 4,500 using JazzCash. Amount was deducted from my account under Ref #TXN-88921, but your website showed an error and no order was generated in my account.'
  );
  const [priority, setPriority] = useState('s1_critical');
  const [category, setCategory] = useState('payment_pending');
  const [orderNumber, setOrderNumber] = useState('ORD-20042');
  const [transactionId, setTransactionId] = useState('TXN-88921');

  // Voice Note File
  const [audioFile, setAudioFile] = useState<File | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleModeChange = (newMode: IngestionMode) => {
    setMode(newMode);
    if (newMode === 'manual') {
      setSubject('Payment deducted via JazzCash but order still missing');
      setPriority('s1_critical');
      setCategory('payment_pending');
    } else if (newMode === 'form') {
      setSubject('Refund not received after 5 business days');
      setPriority('s2_high');
      setCategory('refund_delay');
      setDescription('My return was accepted last week and refund was promised, but my bank account has not received the funds.');
    } else if (newMode === 'email') {
      setSubject('Unable to receive OTP on Telenor number');
      setPriority('s2_high');
      setCategory('login_otp');
      setDescription('From: ahmad.khan@company.com\nTo: support@swiftpay.com\n\nHi team, I am trying to log into my business wallet but SMS OTP is not arriving on my phone.');
    } else if (newMode === 'voice') {
      setSubject('Customer Urdu Voice Note: Payment Kat Chuka Hai');
      setPriority('s2_high');
      setCategory('payment_pending');
      setDescription('Voice Note transcript: "Mera payment kat chuka hai JazzCash se 4500 rupay, lekin website pe order confirm nahi hua. Meharbani karke check karein."');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      if (mode === 'voice' && audioFile) {
        // Multipart Form Submit
        const formData = new FormData();
        formData.append('customer_name', customerName);
        formData.append('customer_email', customerEmail);
        if (customerPhone) formData.append('customer_phone', customerPhone);
        formData.append('subject', subject);
        formData.append('description', description);
        formData.append('priority', priority);
        formData.append('category', category);
        if (orderNumber) formData.append('order_number', orderNumber);
        formData.append('audio_file', audioFile);

        const token = localStorage.getItem('supportswarm_token');
        const res = await fetch('http://127.0.0.1:8000/api/v1/tickets/voice', {
          method: 'POST',
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: formData,
        });

        if (!res.ok) {
          const errData = await res.json().catch(() => ({}));
          throw new Error(errData.detail || 'Failed to upload voice note');
        }

        const data: TicketDetailResponse = await res.json();
        router.push(`/tickets/${data.id}`);
      } else {
        // Standard JSON Submit
        const channelMap: Record<IngestionMode, string> = {
          manual: 'web_chat',
          form: 'support_form',
          email: 'email',
          voice: 'voice_note',
        };

        const payload = {
          customer_name: customerName,
          customer_email: customerEmail,
          customer_phone: customerPhone || undefined,
          channel: channelMap[mode],
          subject,
          description,
          priority,
          category,
          order_number: orderNumber || undefined,
          transaction_id: transactionId || undefined,
        };

        const data = await ApiClient.post<TicketDetailResponse>('/tickets', payload);
        router.push(`/tickets/${data.id}`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to create ticket');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href="/tickets"
            className="p-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-600 transition-colors shadow-xs"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <h1 className="text-xl font-bold text-slate-900 tracking-tight">
              Create New Support Ticket
            </h1>
            <p className="text-xs text-slate-500">
              Omnichannel ingestion into SupportSwarm multi-agent triage loop
            </p>
          </div>
        </div>
      </div>

      {/* Mode Selector Tabs */}
      <div className="bg-white p-2 rounded-2xl border border-slate-200 shadow-xs">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <button
            type="button"
            onClick={() => handleModeChange('manual')}
            className={`flex items-center justify-center gap-2 p-3 rounded-xl text-xs font-semibold transition-all ${
              mode === 'manual'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-700'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            <span>Manual Entry</span>
          </button>

          <button
            type="button"
            onClick={() => handleModeChange('form')}
            className={`flex items-center justify-center gap-2 p-3 rounded-xl text-xs font-semibold transition-all ${
              mode === 'form'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-700'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Support Form</span>
          </button>

          <button
            type="button"
            onClick={() => handleModeChange('email')}
            className={`flex items-center justify-center gap-2 p-3 rounded-xl text-xs font-semibold transition-all ${
              mode === 'email'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-700'
            }`}
          >
            <Mail className="w-4 h-4" />
            <span>Simulated Email</span>
          </button>

          <button
            type="button"
            onClick={() => handleModeChange('voice')}
            className={`flex items-center justify-center gap-2 p-3 rounded-xl text-xs font-semibold transition-all ${
              mode === 'voice'
                ? 'bg-indigo-600 text-white shadow-xs'
                : 'bg-slate-50 hover:bg-slate-100 text-slate-700'
            }`}
          >
            <Mic className="w-4 h-4" />
            <span>Voice Audio Note</span>
          </button>
        </div>
      </div>

      {/* Form Container */}
      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs">
        {error && (
          <div className="mb-5 p-3.5 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-xl flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Customer Profile Section */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              1. Customer Information
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Customer Full Name *
                </label>
                <input
                  type="text"
                  required
                  value={customerName}
                  onChange={(e) => setCustomerName(e.target.value)}
                  className="w-full text-xs px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Customer Email *
                </label>
                <input
                  type="email"
                  required
                  value={customerEmail}
                  onChange={(e) => setCustomerEmail(e.target.value)}
                  className="w-full text-xs px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Phone Number (Optional)
                </label>
                <input
                  type="text"
                  value={customerPhone}
                  onChange={(e) => setCustomerPhone(e.target.value)}
                  placeholder="+923001234567"
                  className="w-full text-xs px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* Issue Details Section */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              2. Complaint Details
            </h3>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Subject Line *
              </label>
              <input
                type="text"
                required
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="w-full text-xs px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 font-medium"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-700 mb-1">
                Customer Message / Complaint Body *
              </label>
              <textarea
                required
                rows={4}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full text-xs px-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 leading-relaxed font-sans"
              />
              <p className="text-[11px] text-slate-400 mt-1">
                PCI Compliance note: Credit card PAN numbers and CVVs are automatically masked before storing.
              </p>
            </div>

            {/* Audio File Upload if Voice Mode */}
            {mode === 'voice' && (
              <div className="p-4 bg-indigo-50/50 border border-dashed border-indigo-300 rounded-xl space-y-2">
                <div className="flex items-center gap-2">
                  <Mic className="w-4 h-4 text-indigo-600" />
                  <span className="text-xs font-bold text-indigo-950">Attach Audio Recording</span>
                </div>
                <p className="text-[11px] text-slate-500">
                  Select an audio file (MP3, WAV, M4A, OGG) to process with OpenAI Whisper speech recognition.
                </p>
                <input
                  type="file"
                  accept="audio/*,.mp3,.wav,.m4a,.ogg"
                  onChange={(e) => setAudioFile(e.target.files?.[0] || null)}
                  className="text-xs text-slate-600 file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700"
                />
              </div>
            )}
          </div>

          <hr className="border-slate-100" />

          {/* Classification & Operational Metadata */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider">
              3. Operational Routing & Mock References
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Category
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full text-xs px-3 py-2 rounded-xl border border-slate-200 bg-slate-50 font-medium text-slate-700"
                >
                  <option value="payment_pending">Payment Pending</option>
                  <option value="duplicate_payment">Duplicate Payment</option>
                  <option value="refund_delay">Refund Delay</option>
                  <option value="login_otp">Login OTP Delay</option>
                  <option value="discount_code">Discount Voucher</option>
                  <option value="order_cancellation">Order Cancellation</option>
                  <option value="delivery_delay">Delivery Delay</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Priority SLA
                </label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value)}
                  className="w-full text-xs px-3 py-2 rounded-xl border border-slate-200 bg-slate-50 font-medium text-slate-700"
                >
                  <option value="s1_critical">S1 Critical (1h SLA)</option>
                  <option value="s2_high">S2 High (4h SLA)</option>
                  <option value="s3_medium">S3 Medium (12h SLA)</option>
                  <option value="s4_low">S4 Low (24h SLA)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Order Number (Optional)
                </label>
                <input
                  type="text"
                  value={orderNumber}
                  onChange={(e) => setOrderNumber(e.target.value)}
                  placeholder="ORD-20042"
                  className="w-full text-xs px-3 py-2 rounded-xl border border-slate-200"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-700 mb-1">
                  Transaction Ref (Optional)
                </label>
                <input
                  type="text"
                  value={transactionId}
                  onChange={(e) => setTransactionId(e.target.value)}
                  placeholder="TXN-88921"
                  className="w-full text-xs px-3 py-2 rounded-xl border border-slate-200"
                />
              </div>
            </div>
          </div>

          <div className="pt-3 flex items-center justify-end gap-3">
            <Link
              href="/tickets"
              className="px-4 py-2 rounded-xl text-xs font-medium text-slate-600 hover:bg-slate-100 transition-colors"
            >
              Cancel
            </Link>

            <button
              type="submit"
              disabled={isSubmitting}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50"
            >
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isSubmitting ? 'Dispatching to AI Swarm...' : 'Create Ticket & Triage'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
