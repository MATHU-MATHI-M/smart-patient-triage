'use client'

import React, { useEffect, useState } from 'react'
import Header from "@/components/Header"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { api } from '@/lib/api'
import { AlertCircle, CheckCircle, Clock, User, ArrowRight, Zap, Filter, MoreHorizontal, Activity } from 'lucide-react'
import { simulatePatient } from '@/lib/simulator'
import Link from 'next/link'

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Loader2, Sparkles, BrainCircuit } from 'lucide-react'

// Types (should be in a shared types file but inline for speed)
type QueueItem = {
    queue_id: number
    priority_score: number
    status: string
    triage_predictions: {
        risk_score: number
        risk_level: string
        patient_visits: {
            visit_id: number
            visit_timestamp: string
            chief_complaint: string
            patients: {
                full_name: string
                age: number
                gender: string
                contact_info: string
            }
        }
    }
}

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

// Helper Component for Status Select
const StatusSelect = ({ status, onChange }: { status: string, onChange: (val: string) => void }) => {
    return (
        <Select value={status} onValueChange={onChange}>
            <SelectTrigger className={`h-9 w-[160px] text-xs font-bold uppercase tracking-wide border shadow-sm transition-all duration-200
                ${status === 'pending' ? 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100' :
                    status === 'treating' ? 'bg-indigo-50 text-indigo-700 border-indigo-200 hover:bg-indigo-100' :
                        status === 'completed' ? 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100' :
                            'bg-white text-slate-700 border-slate-200'
                }
            `}>
                <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent className="bg-white z-50 shadow-xl border-slate-200">
                <SelectItem value="pending" className="text-amber-700 font-medium cursor-pointer hover:bg-amber-50 focus:bg-amber-50">Pending</SelectItem>
                <SelectItem value="treating" className="text-indigo-700 font-medium cursor-pointer hover:bg-indigo-50 focus:bg-indigo-50">Under Treatment</SelectItem>
                <SelectItem value="completed" className="text-emerald-700 font-medium cursor-pointer hover:bg-emerald-50 focus:bg-emerald-50">Completed</SelectItem>
                <SelectItem value="discharged" className="text-slate-700 font-medium cursor-pointer hover:bg-slate-50 focus:bg-slate-50">Discharged</SelectItem>
            </SelectContent>
        </Select>
    )
}

export default function QueuePage() {
    const [queue, setQueue] = useState<QueueItem[]>([])
    const [loading, setLoading] = useState(true)
    const [simulating, setSimulating] = useState(false)
    const [selectedDept, setSelectedDept] = useState("Emergency")

    // Explanation State
    const [explanation, setExplanation] = useState<string | null>(null)
    const [explainingId, setExplainingId] = useState<number | null>(null)
    const [showExplainDialog, setShowExplainDialog] = useState(false)

    // Calculate Average Wait Time for Active Queue (Pending Only)
    const avgWaitTime = queue.length > 0
        ? Math.round(queue.filter(i => i.status === 'pending').reduce((acc, item) => {
            // Ensure timestamp is treated as UTC
            let ts = item.triage_predictions.patient_visits.visit_timestamp;
            if (!ts.endsWith('Z') && !ts.includes('+')) ts += 'Z';

            const visitTime = new Date(ts).getTime();
            const diff = Date.now() - visitTime;
            return acc + diff;
        }, 0) / (queue.filter(i => i.status === 'pending').length || 1) / 60000) // ms to minutes
        : 0;

    async function updateStatus(queueId: number, newStatus: string) {
        // Optimistic UI Update - Remove if completed/discharged/treating (if desired)
        // User requested "delete that particular queue alone" for undertreatment regarding time, 
        // usually this means removing from wait stats, but if they want it removed from view:
        if (newStatus === 'completed' || newStatus === 'discharged') {
            setQueue(prev => prev.filter(item => item.queue_id !== queueId))
        } else {
            setQueue(prev => prev.map(item => item.queue_id === queueId ? { ...item, status: newStatus } : item))
        }

        try {
            await api.patch(`/queue/${queueId}/status?status=${newStatus}`)
        } catch (e) {
            console.error("Failed to update status", e)
            loadQueue() // Revert on error
        }
    }

    async function handleExplain(visitId: number) {
        setExplainingId(visitId)
        setExplanation(null)
        setShowExplainDialog(true)

        try {
            const res = await api.post('/triage-explain', { visit_id: visitId })
            setExplanation(res.data.explanation)
        } catch (e: any) {
            console.error("Explanation Failed", e)
            setExplanation("Failed to generate explanation. Please try again.")
        } finally {
            setExplainingId(null)
        }
    }

    const DEPARTMENTS = [
        "Emergency",
        "Cardiology",
        "Respiratory",
        "Neurology",
        "General Medicine",
        "Orthopedics"
    ]

    async function loadQueue() {
        try {
            const { data } = await api.get(`/queues/${selectedDept}`)
            setQueue(data.queue || [])
        } catch (e) {
            console.error(e)
            setQueue([])
        } finally {
            setLoading(false)
        }
    }

    async function handleSimulate() {
        setSimulating(true)
        await simulatePatient();
        await loadQueue();
        setSimulating(false)
    }

    useEffect(() => {
        loadQueue()
        const int = setInterval(loadQueue, 5000)
        return () => clearInterval(int)
    }, [selectedDept]) // Reload when dept changes

    function getRiskColor(level: string, score: number) {
        if (score > 0.7 || level === 'High') return 'bg-red-50 border-red-500 text-red-700'
        if (score > 0.4 || level === 'Medium') return 'bg-amber-50 border-amber-500 text-amber-700'
        return 'bg-emerald-50 border-emerald-500 text-emerald-700'
    }

    function getScoreColor(score: number) {
        if (score > 0.7) return 'text-red-600'
        if (score > 0.4) return 'text-amber-600'
        return 'text-emerald-600'
    }

    // Time Formatter handling UTC
    function formatVisitTime(ts: string) {
        if (!ts) return '';
        // Force UTC if no timezone info
        if (!ts.endsWith('Z') && !ts.includes('+')) ts += 'Z';
        return new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }

    return (
        <div className="min-h-screen bg-[#f8fafc] font-sans text-slate-900 selection:bg-indigo-100">
            <Header />
            <main className="max-w-7xl mx-auto p-6 md:p-8 space-y-8 animate-in fade-in duration-700 slide-in-from-bottom-4">

                {/* Header Actions 3D */}
                <div className="flex flex-col md:flex-row justify-between items-end mb-8 border-b border-slate-200 pb-6 gap-6">
                    <div className="space-y-2">
                        <div className="flex items-center gap-3">
                            <div className="p-2.5 bg-slate-900 rounded-xl shadow-lg shadow-slate-900/20">
                                <Activity className="h-6 w-6 text-white" />
                            </div>
                            <h1 className="text-3xl font-bold tracking-tight text-slate-900">
                                Department Queues
                            </h1>
                        </div>
                        <div className="flex items-center gap-4 text-slate-500 font-medium">
                            <p>Live prioritization based on ML risk assessment.</p>
                            <span className="h-1 w-1 rounded-full bg-slate-300"></span>
                            <div className="flex items-center gap-2 text-indigo-600 font-bold bg-indigo-50 px-3 py-1 rounded-full text-xs uppercase tracking-wide">
                                <Clock size={14} />
                                <span>Avg Wait: {avgWaitTime} min</span>
                            </div>
                        </div>
                    </div>

                    <div className="flex gap-4">
                        <Button variant="outline" onClick={handleSimulate} disabled={simulating} className="h-11 px-5 border-slate-200 text-slate-600 font-semibold bg-white hover:bg-slate-50 hover:text-slate-900 transition-all rounded-lg shadow-sm">
                            <Zap className={`mr-2 h-4 w-4 ${simulating ? 'animate-spin text-amber-500' : 'text-slate-400 group-hover:text-amber-500'}`} />
                            {simulating ? "Generating..." : "Simulate Arrival"}
                        </Button>
                        <Button variant="outline" className="h-11 px-5 border-slate-200 text-slate-600 font-semibold bg-white hover:bg-slate-50 hover:text-slate-900 transition-all rounded-lg shadow-sm">
                            <Filter className="mr-2 h-4 w-4 text-slate-400" /> Filter
                        </Button>
                    </div>
                </div>

                {/* Department Selector - Pill Tabs */}
                <div className="flex flex-wrap gap-2 pb-4">
                    {DEPARTMENTS.map(dept => (
                        <button
                            key={dept}
                            onClick={() => setSelectedDept(dept)}
                            className={`relative px-5 py-2.5 rounded-full text-sm font-bold transition-all duration-300 border
                                ${selectedDept === dept
                                    ? 'bg-slate-900 text-white border-slate-900 shadow-md shadow-slate-900/20 hover:-translate-y-0.5'
                                    : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 hover:border-slate-300'
                                }`}
                        >
                            <span className="flex items-center gap-2">
                                {dept}
                                {selectedDept === dept && (
                                    <span className="flex h-5 items-center justify-center px-1.5 rounded-full bg-slate-800 text-[10px] text-white">
                                        {queue.length}
                                    </span>
                                )}
                            </span>
                        </button>
                    ))}
                </div>

                {/* Queue List */}
                <div className="space-y-4">
                    {queue.length === 0 && !loading && (
                        <div className="text-center py-20 bg-white rounded-3xl border border-dashed border-slate-200">
                            <div className="mx-auto h-16 w-16 bg-slate-50 rounded-full flex items-center justify-center mb-4">
                                <User className="h-8 w-8 text-slate-300" />
                            </div>
                            <h3 className="text-lg font-bold text-slate-900">Queue is Empty</h3>
                            <p className="text-slate-500 mb-6 max-w-sm mx-auto">No active patients currently waiting in {selectedDept}.</p>
                            <Button onClick={handleSimulate} className="bg-slate-900 text-white px-6 py-2 rounded-lg font-bold shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all">
                                <Zap className="mr-2 h-4 w-4 text-amber-400" /> Simulate Patient Arrival
                            </Button>
                        </div>
                    )}

                    {queue.map((item) => {
                        const p = item.triage_predictions.patient_visits.patients
                        const v = item.triage_predictions.patient_visits
                        const pred = item.triage_predictions

                        // Risk Logic (Cleaned up)
                        const isHigh = pred.risk_score > 0.7 || pred.risk_level === 'High';
                        const isMedium = !isHigh && (pred.risk_score > 0.4 || pred.risk_level === 'Medium');

                        const riskColor = isHigh ? 'text-red-600' : isMedium ? 'text-amber-600' : 'text-emerald-600';
                        const riskBg = isHigh ? 'bg-red-50' : isMedium ? 'bg-amber-50' : 'bg-emerald-50';
                        const borderColor = isHigh ? 'border-red-100' : isMedium ? 'border-amber-100' : 'border-emerald-100';
                        const riskBar = isHigh ? 'bg-red-500' : isMedium ? 'bg-amber-500' : 'bg-emerald-500';

                        return (
                            <div key={item.queue_id} className="group relative bg-white rounded-xl shadow-sm border border-slate-200 transition-all duration-300 hover:shadow-lg hover:border-slate-300 hover:-translate-y-0.5 overflow-hidden">
                                {/* Risk Bar Indicator */}
                                <div className={`absolute left-0 top-0 bottom-0 w-1 ${riskBar}`}></div>

                                <div className="flex flex-col md:flex-row p-5 pl-7 gap-6 items-start md:items-center">

                                    {/* Patient Info */}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-3 mb-1">
                                            <h3 className="text-lg font-bold text-slate-900 truncate">{p.full_name}</h3>
                                            <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-500 text-xs font-bold uppercase tracking-wider">{p.age} • {p.gender}</span>
                                        </div>
                                        {/* AI Explain Button */}
                                        <div className="flex items-center gap-2 mt-2">
                                            <div className="flex items-start gap-2 text-slate-600 text-sm font-medium">
                                                <AlertCircle className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
                                                <p className="line-clamp-2">{v.chief_complaint}</p>
                                            </div>
                                            <button
                                                onClick={() => handleExplain(item.triage_predictions.patient_visits['visit_id'] || 0)}
                                                className="ml-2 text-xs font-bold text-indigo-600 flex items-center gap-1 hover:underline hover:text-indigo-700 bg-indigo-50 px-3 py-1 rounded-full border border-indigo-100 transition-all shadow-sm"
                                            >
                                                <Sparkles size={12} /> View Analysis
                                            </button>
                                        </div>
                                        <div className="flex items-center gap-4 mt-3 text-xs font-bold text-slate-400 uppercase tracking-wide">
                                            <span className="flex items-center gap-1.5"><Clock size={14} /> {formatVisitTime(v.visit_timestamp)}</span>
                                            <span className="hidden sm:flex items-center gap-1.5"><User size={14} /> {p.contact_info || 'No Contact'}</span>
                                        </div>
                                    </div>

                                    {/* Risk & Status */}
                                    <div className="flex flex-row md:flex-col items-center md:items-end gap-4 md:gap-1 shrink-0 w-full md:w-auto justify-between md:justify-end border-t md:border-t-0 p-4 md:p-0 md:bg-transparent bg-slate-50 -mx-5 -mb-5 md:mx-0 md:mb-0 mt-2 md:mt-0">

                                        {/* Risk Score */}
                                        <div className="flex items-center gap-3 md:gap-2">
                                            <div className="text-right hidden md:block">
                                                <div className="text-[10px] font-bold text-slate-400 uppercase">Risk Level</div>
                                                <div className={`text-sm font-black ${riskColor}`}>{pred.risk_level}</div>
                                            </div>
                                            <div className={`flex flex-col items-center justify-center h-12 w-16 rounded-lg border ${borderColor} ${riskBg}`}>
                                                <span className={`text-xl font-black leading-none ${riskColor}`}>{(pred.risk_score * 100).toFixed(0)}</span>
                                                <span className="text-[9px] font-bold text-slate-400">SCORE</span>
                                            </div>
                                        </div>

                                        {/* Mobile Status Select */}
                                        <div className="md:hidden">
                                            <StatusSelect
                                                status={item.status}
                                                onChange={(val) => updateStatus(item.queue_id, val)}
                                            />
                                        </div>
                                    </div>

                                    {/* Actions / Status Display (Desktop) */}
                                    <div className="hidden md:flex flex-col gap-2 shrink-0 min-w-[170px] items-end">
                                        <StatusSelect
                                            status={item.status}
                                            onChange={(val) => updateStatus(item.queue_id, val)}
                                        />
                                    </div>

                                </div>
                            </div>
                        )
                    })}
                </div>

                {/* AI Explanation Dialog */}
                <Dialog open={showExplainDialog} onOpenChange={setShowExplainDialog}>
                    <DialogContent className="sm:max-w-md bg-white rounded-2xl border-0 shadow-2xl">
                        <DialogHeader>
                            <DialogTitle className="flex items-center gap-2 text-xl font-bold text-slate-900">
                                <Sparkles className="text-indigo-600" size={20} />
                                Clinical Decision Support
                            </DialogTitle>
                            <DialogDescription className="text-slate-500 font-medium">
                                AI-generated analysis of risk factors and triage reasoning.
                            </DialogDescription>
                        </DialogHeader>

                        <div className="py-2">
                            {explainingId ? (
                                <div className="flex flex-col items-center justify-center space-y-4 py-12">
                                    <Loader2 className="h-10 w-10 animate-spin text-indigo-600" />
                                    <div className="text-center space-y-1">
                                        <p className="text-sm font-bold text-slate-900">Analyzing Patient Data...</p>
                                        <p className="text-xs text-slate-500">Consulting ML Engine & Clinical Models</p>
                                    </div>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    <div className="bg-indigo-50/50 p-5 rounded-xl border border-indigo-100">
                                        <h4 className="text-xs font-bold text-indigo-900 uppercase tracking-wider mb-3 flex items-center gap-2">
                                            <BrainCircuit size={14} /> AI Analysis
                                        </h4>
                                        {explanation ? (
                                            <div className="text-slate-700 text-sm leading-relaxed font-medium whitespace-pre-line text-justify">
                                                {explanation.split(/\*\*(.*?)\*\*/g).map((part, index) =>
                                                    index % 2 === 1 ? <strong key={index} className="text-indigo-900 font-bold">{part}</strong> : part
                                                )}
                                            </div>
                                        ) : (
                                            <p className="text-center text-slate-400 italic text-sm">Analysis currently unavailable.</p>
                                        )}
                                    </div>

                                    <div className="text-[10px] text-slate-400 text-center font-medium">
                                        * This is an automated assessment to assist, not replace, clinical judgment.
                                    </div>
                                </div>
                            )}
                        </div>

                        <DialogFooter>
                            <Button onClick={() => setShowExplainDialog(false)} className="w-full bg-slate-900 text-white font-bold hover:bg-slate-800 rounded-xl h-11">
                                Close Analysis
                            </Button>
                        </DialogFooter>
                    </DialogContent>
                </Dialog>

            </main>
        </div>
    )
}
