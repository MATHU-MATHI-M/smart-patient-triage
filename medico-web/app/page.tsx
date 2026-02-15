'use client'

import React, { useEffect, useState } from 'react'
import Header from "@/components/Header"
import { Card, CardHeader, CardTitle, CardContent, CardDescription } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { api } from '@/lib/api'
import { Activity, Clock, Users, ArrowRight, TrendingUp, Zap, PlusCircle, LayoutDashboard, Stethoscope, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import { simulatePatient } from '@/lib/simulator'
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts'

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_patients: 0,
    active_visits: 0,
    high_risk_patients: 0,
    medium_risk_patients: 0,
    low_risk_patients: 0,
    avg_wait_time: 0
  })

  // Department Load Data for Charts
  const [deptData, setDeptData] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [simulating, setSimulating] = useState(false)

  // Fetch Logic
  async function loadData() {
    try {
      // 1. Overall Stats
      const { data: overall } = await api.get('/dashboard/stats')
      setStats(overall)

      // 2. Department Loads (Parallel Fetch)
      const depts = ['Emergency', 'Cardiology', 'General Medicine', 'Neurology', 'Orthopedics']
      const queues = await Promise.all(depts.map(d => api.get(`/queues/${d}`).catch(() => ({ data: { queue: [] } }))))

      const chartData = depts.map((d, i) => ({
        name: d,
        patients: queues[i].data.queue?.length || 0,
        capacity: d === 'Emergency' ? 20 : 15 // Mock capacity
      }))
      setDeptData(chartData)

    } catch (e) {
      console.error("Dashboard Load Error", e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    let isMounted = true;
    loadData();
    const interval = setInterval(() => {
      if (isMounted) loadData();
    }, 5000); // Live update

    return () => {
      isMounted = false;
      clearInterval(interval);
    }
  }, [])

  async function handleSimulate() {
    setSimulating(true)
    for (let i = 0; i < 3; i++) {
      await simulatePatient();
    }
    await loadData();
    setSimulating(false)
  }

  // Visual Configs
  const statCards = [
    { label: "High Risk Alerts", value: stats.high_risk_patients, icon: Activity, color: "text-red-600", bg: "bg-red-50", border: "border-red-200", note: "Critical Attention" },
    { label: "Active Visits", value: stats.active_visits, icon: Stethoscope, color: "text-blue-600", bg: "bg-blue-50", border: "border-blue-200", note: "Currently in Triage" },
    { label: "Avg Wait Time", value: `${stats.avg_wait_time}m`, icon: Clock, color: "text-amber-600", bg: "bg-amber-50", border: "border-amber-200", note: "Slightly Elevated" },
  ]

  return (
    <div className="min-h-screen bg-[#f8fafc] font-sans selection:bg-blue-100">
      <Header />

      <main className="max-w-7xl mx-auto p-6 md:p-8 space-y-10 animate-in fade-in duration-700 slide-in-from-bottom-4">

        {/* --- Hero Section: Clean & Authoritative --- */}
        <div className="flex flex-col lg:flex-row justify-between items-end gap-6 pb-2 border-b border-slate-200/60">
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <div className="p-2.5 bg-slate-900 rounded-xl shadow-lg shadow-slate-900/20">
                <LayoutDashboard className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-4xl font-bold tracking-tight text-slate-900">
                Command Center
              </h1>
            </div>
            <p className="text-lg text-slate-500 font-medium max-w-2xl leading-relaxed">
              Real-time operational oversight and AI-driven triage analytics.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-emerald-50 rounded-full border border-emerald-100 text-emerald-700 font-bold text-sm shadow-sm">
              <span className="relative flex h-2.5 w-2.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              System Operational
            </div>
            <Button
              variant="outline"
              onClick={handleSimulate}
              disabled={simulating}
              className="h-11 px-5 border-slate-200 text-slate-600 font-semibold bg-white hover:bg-slate-50 hover:text-slate-900 transition-all rounded-lg"
            >
              {simulating ? <Zap className="mr-2 h-4 w-4 animate-spin text-amber-500" /> : <Zap className="mr-2 h-4 w-4 text-slate-400 group-hover:text-amber-500" />}
              {simulating ? "Simulating Traffic..." : "Test Traffic"}
            </Button>
          </div>
        </div>

        {/* --- Actions Row: Physical Buttons --- */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Link href="/register" className="group">
            <div className="relative overflow-hidden bg-white hover:bg-slate-50 border border-slate-200 rounded-2xl p-6 transition-all duration-300 hover:shadow-xl hover:-translate-y-1 group hover:border-blue-200 cursor-pointer perspective-1000">
              <div className="flex items-center justify-between relative z-10 transition-transform duration-300 group-hover:bg-slate-50">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-blue-50 flex items-center justify-center text-blue-600 group-hover:scale-110 transition-transform duration-300">
                    <Users size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">Register Patient</h3>
                    <p className="text-sm text-slate-500 font-medium">New walk-in or ambulance arrival.</p>
                  </div>
                </div>
                <div className="h-10 w-10 rounded-full border border-slate-100 flex items-center justify-center text-slate-300 group-hover:bg-blue-600 group-hover:text-white group-hover:border-blue-600 transition-all duration-300">
                  <ArrowRight size={18} />
                </div>
              </div>
            </div>
          </Link>

          <Link href="/triage" className="group">
            <div className="relative overflow-hidden bg-slate-900 hover:bg-slate-800 border border-slate-900 rounded-2xl p-6 transition-all duration-300 hover:shadow-2xl hover:shadow-slate-900/20 hover:-translate-y-1 cursor-pointer perspective-1000">
              <div className="absolute top-0 right-0 p-3 opacity-10">
                <PlusCircle size={100} className="text-white transform translate-x-10 -translate-y-10" />
              </div>
              <div className="flex items-center justify-between relative z-10">
                <div className="flex items-center gap-4">
                  <div className="h-12 w-12 rounded-full bg-slate-800 flex items-center justify-center text-emerald-400 group-hover:scale-110 transition-transform duration-300">
                    <PlusCircle size={24} />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white">Start Triage</h3>
                    <p className="text-sm text-slate-400 font-medium">Evaluate symptoms & assign priority.</p>
                  </div>
                </div>
                <div className="h-10 w-10 rounded-full bg-slate-800 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500 group-hover:text-white transition-all duration-300">
                  <ArrowRight size={18} />
                </div>
              </div>
            </div>
          </Link>
        </div>

        {/* --- Metrics Grid: Tightly grouped, subtle gradients --- */}
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {statCards.map((s, i) => (
            <div key={i} className="group relative perspective-1000">
              <Card className="h-full border-slate-200 bg-white shadow-sm hover:shadow-2xl transition-all duration-300 ease-out hover:-translate-y-1 hover:rotate-x-2 relative overflow-hidden">
                <div className={`absolute top-0 right-0 w-24 h-24 bg-gradient-to-br ${s.gradient} opacity-5 group-hover:opacity-10 rounded-bl-full transition-opacity duration-300`}></div>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-bold text-slate-500 uppercase tracking-wide">{s.label}</CardTitle>
                  <s.icon className={`h-5 w-5 ${s.color} opacity-70 group-hover:opacity-100 transition-opacity`} />
                </CardHeader>
                <CardContent>
                  <div className="text-4xl font-extrabold text-slate-900 tracking-tight">{loading ? "..." : s.value}</div>
                  <div className="flex items-center mt-3">
                    <div className={`text-xs font-bold px-2 py-1 rounded-md bg-opacity-10 ${s.bg} ${s.color.replace('text-', 'text-opacity-80 text-')}`}>
                      {s.note}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          ))}

          {/* System Health Compact Card */}
          <Card className="bg-slate-50 border-slate-200 shadow-sm hover:shadow-md transition-all duration-300">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-bold text-slate-500 uppercase flex items-center gap-2">
                <Activity size={16} /> Backend Status
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex justify-between items-center text-sm font-medium">
                <span className="text-slate-600">ML Engine</span>
                <div className="flex items-center gap-2 text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">
                  <span className="relative flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </span>
                  Active
                </div>
              </div>
              <Link href="/queue" className="block w-full">
                <Button variant="ghost" size="sm" className="w-full justify-between hover:bg-white hover:shadow-sm border border-transparent hover:border-slate-100 text-slate-600 group">
                  Monitor Queues <ChevronRight size={14} className="group-hover:translate-x-1 transition-transform" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* --- Analytics Section --- */}
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-7">
          {/* Main Chart */}
          <Card className="col-span-1 lg:col-span-4 border-slate-200 shadow-sm hover:shadow-xl transition-all duration-500 rounded-2xl overflow-hidden">
            <CardHeader className="border-b border-slate-100 bg-slate-50/30">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-bold text-slate-800">Department Load</CardTitle>
                  <CardDescription className="text-slate-500 font-medium mt-1">Real-time patient distribution.</CardDescription>
                </div>
                <div className="p-2 bg-white border border-slate-200 rounded-lg shadow-sm text-slate-500">
                  <TrendingUp size={20} />
                </div>
              </div>
            </CardHeader>
            <CardContent className="p-6 h-[400px]">
              {loading ? (
                <div className="h-full flex items-center justify-center text-slate-400 font-medium animate-pulse">Loading Analytics...</div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={deptData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b', fontWeight: 600 }} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} />
                    <Tooltip
                      cursor={{ fill: '#f8fafc' }}
                      contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)', padding: '12px 16px', fontWeight: 'bold' }}
                    />
                    <Bar dataKey="patients" fill="#3b82f6" radius={[6, 6, 0, 0]} barSize={40} animationDuration={1000} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          {/* Risk Distribution Chart */}
          <Card className="col-span-1 lg:col-span-3 border-slate-200 shadow-sm hover:shadow-xl transition-all duration-500 rounded-2xl overflow-hidden">
            <CardHeader className="border-b border-slate-100 bg-slate-50/30">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg font-bold text-slate-800">Risk Segmentation</CardTitle>
                  <CardDescription className="text-slate-500 font-medium mt-1">Live triage categorization.</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent className="h-[400px] flex items-center justify-center relative bg-white">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={[
                      { name: 'High Risk', value: stats.high_risk_patients, color: '#ef4444' },
                      { name: 'Medium Risk', value: stats.medium_risk_patients, color: '#f59e0b' },
                      { name: 'Low Risk', value: stats.low_risk_patients, color: '#10b981' },
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={85}
                    outerRadius={120}
                    paddingAngle={3}
                    dataKey="value"
                    stroke="none"
                    cornerRadius={6}
                  >
                    <Cell fill="#ef4444" />
                    <Cell fill="#fcd34d" />
                    <Cell fill="#4ade80" />
                  </Pie>
                  <Tooltip contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)', fontWeight: 'bold' }} />
                  <Legend verticalAlign="bottom" height={36} iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none pb-12">
                <span className="text-5xl font-black text-slate-800 tracking-tighter">{stats.active_visits}</span>
                <span className="text-xs text-slate-400 font-bold uppercase tracking-widest mt-1">Total Cases</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}
