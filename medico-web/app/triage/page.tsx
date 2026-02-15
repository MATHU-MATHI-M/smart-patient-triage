'use client'

import React, { useState } from 'react'
import Header from "@/components/Header"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { api } from '@/lib/api'
import { Activity, Search, UserPlus, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import VisitForm from "@/components/VisitForm"

// Types
type Patient = {
    patient_id: number
    full_name: string
    age: number
    gender: string
    contact_info: string
}
type HistoryItem = {
    condition_name: string
    is_chronic: boolean
    notes: string
    diagnosis_date?: string
}

export default function TriagePage() {
    const [searchName, setSearchName] = useState('')
    const [searchEmail, setSearchEmail] = useState('')
    const [patient, setPatient] = useState<Patient | null>(null)
    const [history, setHistory] = useState<HistoryItem[]>([])

    const [mode, setMode] = useState<'search' | 'register' | 'visit'>('search')
    const [loading, setLoading] = useState(false)

    // Registration State
    const [regForm, setRegForm] = useState<{ name: string, age: number | string, gender: string, email: string, history: HistoryItem[] }>({ name: '', age: 30, gender: 'Male', email: '', history: [] })

    // ... (existing code)


    // History Input State
    const [hInput, setHInput] = useState({ cond: '', chronic: false, note: '', date: '' })

    async function handleSearch() {
        setLoading(true)
        setPatient(null)
        setHistory([])
        try {
            const { data } = await api.get('/patients/lookup', { params: { name: searchName, email: searchEmail } })
            if (data.patients && data.patients.length > 0) {
                const p = data.patients[0]
                setPatient(p)
                // Fetch History
                const hRes = await api.get(`/patients/${p.patient_id}/history`)
                setHistory(hRes.data.history || [])
                setMode('visit')
            } else {
                // Pre-fill reg form
                setRegForm({ ...regForm, name: searchName, email: searchEmail })
                setMode('register')
            }
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    async function handleRegister() {
        if (regForm.history.length === 0) {
            alert("Medical History is Mandatory!")
            return
        }
        setLoading(true)
        try {
            const payload = {
                full_name: regForm.name,
                age: Number(regForm.age),
                gender: regForm.gender,
                contact_info: regForm.email,
                medical_history: regForm.history
            }
            const { data } = await api.post('/patients', payload)
            // Success
            setPatient({ ...payload, patient_id: data.patient_id })
            setHistory(regForm.history)
            setMode('visit')
        } catch (e) {
            alert("Registration Failed")
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-[#f8fafc] font-sans selection:bg-indigo-100 text-slate-900">
            <Header />
            <main className="max-w-6xl mx-auto p-6 md:p-8 space-y-8 animate-in fade-in duration-700 slide-in-from-bottom-4">

                {/* Header Section: Minimal & Functional */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 pb-6 border-b border-slate-200">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-slate-900 flex items-center gap-3">
                            <span className="p-2 bg-slate-900 rounded-lg text-white shadow-md shadow-slate-900/20">
                                <UserPlus size={24} />
                            </span>
                            Patient Admission
                        </h1>
                        <p className="mt-2 text-lg text-slate-500 max-w-2xl">
                            Search existing records or register new walk-in patients.
                        </p>
                    </div>
                    {mode !== 'search' && (
                        <Button variant="ghost" onClick={() => setMode('search')} className="text-slate-500 hover:text-slate-900 hover:bg-slate-100">
                            Cancel & Return to Search
                        </Button>
                    )}
                </div>

                {/* Step 1: Search - Focused & Clean */}
                {mode === 'search' && (
                    <div className="max-w-2xl mx-auto pt-8">
                        <Card className="border-0 shadow-xl shadow-slate-200/60 rounded-2xl overflow-hidden bg-white hover:shadow-2xl transition-all duration-500 hover:-translate-y-1">
                            <div className="bg-slate-50/50 p-8 border-b border-slate-100">
                                <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
                                    <Search className="w-5 h-5 text-indigo-500" />
                                    Find Patient Record
                                </h2>
                            </div>
                            <CardContent className="p-8 space-y-6">
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-slate-700 uppercase tracking-wide ml-1">Full Name</label>
                                        <div className="relative">
                                            <Search className="absolute left-4 top-3.5 h-5 w-5 text-slate-400" />
                                            <Input
                                                className="pl-12 h-14 text-lg bg-slate-50 border-slate-200 focus:border-indigo-500 focus:ring-indigo-500/20 rounded-xl transition-all shadow-sm"
                                                placeholder="e.g. John Doe"
                                                value={searchName}
                                                onChange={e => setSearchName(e.target.value)}
                                            />
                                        </div>
                                    </div>
                                    <div className="space-y-2">
                                        <label className="text-sm font-semibold text-slate-700 uppercase tracking-wide ml-1">Email / ID</label>
                                        <Input
                                            className="h-14 text-lg bg-slate-50 border-slate-200 focus:border-indigo-500 focus:ring-indigo-500/20 rounded-xl transition-all shadow-sm"
                                            placeholder="Optional identifier..."
                                            value={searchEmail}
                                            onChange={e => setSearchEmail(e.target.value)}
                                        />
                                    </div>
                                </div>
                                <Button
                                    onClick={handleSearch}
                                    disabled={loading}
                                    className="w-full h-14 text-lg font-bold bg-slate-900 hover:bg-slate-800 text-white rounded-xl shadow-lg shadow-slate-900/10 hover:shadow-xl hover:-translate-y-0.5 transition-all"
                                >
                                    {loading ? "Searching..." : "Search Records"}
                                </Button>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {/* Step 2: Register - Medical Form Style */}
                {mode === 'register' && (
                    <div className="max-w-4xl mx-auto">
                        <Card className="border-0 shadow-2xl shadow-slate-200/60 rounded-3xl overflow-hidden bg-white animate-in zoom-in-95 duration-300">
                            <div className="h-1.5 bg-indigo-500 w-full"></div>
                            <CardHeader className="bg-slate-50/50 pb-6 pt-8 px-10 border-b border-slate-100">
                                <CardTitle className="flex items-center gap-3 text-2xl font-bold text-slate-900">
                                    New Registration
                                </CardTitle>
                                <p className="text-slate-500 font-medium">Create a new patient profile. All fields marked <span className="text-red-500">*</span> are required.</p>
                            </CardHeader>
                            <CardContent className="p-10 space-y-10">
                                {/* Section: Personal Info */}
                                <div className="space-y-6">
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className="h-8 w-8 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold border border-indigo-100">1</div>
                                        <h3 className="text-lg font-bold text-slate-800">Demographics</h3>
                                    </div>

                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="space-y-2">
                                            <label className="text-sm font-semibold text-slate-600">Full Name <span className="text-red-500">*</span></label>
                                            <Input className="h-12 bg-white border-slate-200 focus:border-indigo-500 rounded-lg" placeholder="Legal Name" value={regForm.name} onChange={e => setRegForm({ ...regForm, name: e.target.value })} />
                                        </div>
                                        <div className="space-y-2">
                                            <label className="text-sm font-semibold text-slate-600">Contact / Email</label>
                                            <Input className="h-12 bg-white border-slate-200 focus:border-indigo-500 rounded-lg" placeholder="Email or Phone" value={regForm.email} onChange={e => setRegForm({ ...regForm, email: e.target.value })} />
                                        </div>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="space-y-2">
                                                <label className="text-sm font-semibold text-slate-600">Age <span className="text-red-500">*</span></label>
                                                <Input className="h-12 bg-white border-slate-200 focus:border-indigo-500 rounded-lg" type="number" placeholder="Years" value={regForm.age} onChange={e => setRegForm({ ...regForm, age: e.target.value === '' ? '' : parseInt(e.target.value) })} />
                                            </div>
                                            <div className="space-y-2">
                                                <label className="text-sm font-semibold text-slate-600">Gender <span className="text-red-500">*</span></label>
                                                <select className="flex h-12 w-full items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50" value={regForm.gender} onChange={e => setRegForm({ ...regForm, gender: e.target.value })}>
                                                    <option>Male</option><option>Female</option><option>Other</option>
                                                </select>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div className="w-full h-px bg-slate-100"></div>

                                {/* Section: Medical History */}
                                <div className="space-y-6">
                                    <div className="flex items-center gap-2 mb-4">
                                        <div className="h-8 w-8 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold border border-indigo-100">2</div>
                                        <h3 className="text-lg font-bold text-slate-800">Medical History</h3>
                                    </div>

                                    <div className="bg-slate-50 p-6 rounded-2xl border border-slate-200/60">
                                        {/* History List */}
                                        {regForm.history.length > 0 && (
                                            <div className="mb-6 space-y-2">
                                                {regForm.history.map((h, i) => (
                                                    <div key={i} className="flex justify-between items-center bg-white p-3 px-4 rounded-lg border border-slate-200 shadow-sm">
                                                        <div className="flex items-center gap-3">
                                                            <span className="font-semibold text-slate-800">{h.condition_name}</span>
                                                            {h.is_chronic && <span className="text-amber-600 text-[10px] font-bold px-2 py-0.5 bg-amber-50 rounded-full uppercase tracking-wide border border-amber-100">Chronic</span>}
                                                        </div>
                                                        <span className="text-slate-400 text-xs font-mono">{h.diagnosis_date}</span>
                                                    </div>
                                                ))}
                                            </div>
                                        )}

                                        {/* Add History Form */}
                                        <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-end">
                                            <div className="md:col-span-4 space-y-1.5">
                                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wide">Condition</label>
                                                <Input placeholder="e.g. Hypertension" className="h-10 bg-white border-slate-300" value={hInput.cond} onChange={e => setHInput({ ...hInput, cond: e.target.value })} />
                                            </div>
                                            <div className="md:col-span-3 space-y-1.5">
                                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wide">Approx Date</label>
                                                <Input type="date" className="h-10 bg-white border-slate-300" value={hInput.date} onChange={e => setHInput({ ...hInput, date: e.target.value })} />
                                            </div>
                                            <div className="md:col-span-3 space-y-1.5">
                                                <label className="text-xs font-bold text-slate-500 uppercase tracking-wide">Notes</label>
                                                <Input placeholder="Optional..." className="h-10 bg-white border-slate-300" value={hInput.note} onChange={e => setHInput({ ...hInput, note: e.target.value })} />
                                            </div>
                                            <div className="md:col-span-2 flex flex-col gap-2">
                                                <label className="flex items-center text-xs text-slate-700 font-bold cursor-pointer select-none h-6">
                                                    <input type="checkbox" className="mr-2 h-4 w-4 rounded accent-indigo-600" checked={hInput.chronic} onChange={e => setHInput({ ...hInput, chronic: e.target.checked })} /> Chronic
                                                </label>
                                                <Button size="sm" className="w-full h-10 bg-white hover:bg-slate-50 text-indigo-600 border border-indigo-200 font-bold" onClick={() => {
                                                    if (!hInput.cond) return;
                                                    setRegForm({
                                                        ...regForm, history: [...regForm.history, {
                                                            condition_name: hInput.cond, is_chronic: hInput.chronic, notes: hInput.note, diagnosis_date: hInput.date
                                                        }]
                                                    })
                                                    setHInput({ cond: '', chronic: false, note: '', date: '' })
                                                }}>+ Add</Button>
                                            </div>
                                        </div>
                                    </div>
                                    {regForm.history.length === 0 && (
                                        <div className="flex items-center gap-2 text-amber-600 text-sm font-medium bg-amber-50 px-4 py-3 rounded-lg border border-amber-100">
                                            <AlertCircle size={16} /> At least one history item is recommended for accurate risk scoring.
                                        </div>
                                    )}
                                </div>

                                <div className="pt-6 flex gap-4">
                                    <Button variant="outline" className="flex-1 h-14 text-slate-600 font-bold border-slate-200 hover:bg-slate-50 hover:text-slate-900" onClick={() => setMode('search')}>
                                        Cancel
                                    </Button>
                                    <Button className="flex-[2] h-14 bg-indigo-600 hover:bg-indigo-700 text-white font-bold text-lg shadow-xl shadow-indigo-200 hover:shadow-indigo-300 hover:-translate-y-0.5 transition-all rounded-xl" onClick={handleRegister} disabled={loading}>
                                        {loading ? "Registering..." : "Complete Registration"}
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    </div>
                )}

                {/* Step 3: Visit Form - Premium Layout */}
                {mode === 'visit' && patient && (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-6 duration-700">
                        {/* Patient Identity Banner */}
                        <Card className="border-0 bg-slate-900 text-white shadow-2xl shadow-slate-900/20 rounded-2xl overflow-hidden relative">
                            {/* Texture */}
                            <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20"></div>
                            <div className="absolute top-0 right-0 p-12 opacity-5">
                                <Activity size={200} className="text-white" />
                            </div>

                            <CardContent className="p-8 md:p-10 flex flex-col md:flex-row justify-between items-center relative z-10">
                                <div className="space-y-4">
                                    <div className="flex items-center gap-3">
                                        <div className="h-12 w-12 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                                            <CheckCircle size={24} />
                                        </div>
                                        <div>
                                            <h2 className="text-3xl font-bold tracking-tight text-white">{patient.full_name}</h2>
                                            <div className="flex gap-3 text-slate-400 text-sm font-medium mt-1">
                                                <span>ID: {patient.patient_id}</span>
                                                <span>•</span>
                                                <span className="text-slate-300">{patient.age} Years, {patient.gender}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <Button className="mt-6 md:mt-0 bg-white/10 hover:bg-white/20 text-white border border-white/10 backdrop-blur-sm h-12 px-6 rounded-xl font-semibold transition-all" onClick={() => setMode('search')}>
                                    Change Patient
                                </Button>
                            </CardContent>
                        </Card>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                            {/* History Sidebar */}
                            <Card className="lg:col-span-1 border-0 shadow-lg shadow-slate-200/50 rounded-2xl h-fit bg-white">
                                <CardHeader className="bg-slate-50/50 border-b border-slate-100 py-4 px-6">
                                    <CardTitle className="text-xs font-extrabold uppercase tracking-widest text-slate-400">Medical Profile</CardTitle>
                                </CardHeader>
                                <CardContent className="p-0">
                                    {history.length > 0 ? (
                                        <div className="divide-y divide-slate-100">
                                            {history.map((h, i) => (
                                                <div key={i} className="p-5 hover:bg-slate-50 transition-colors group">
                                                    <div className="flex justify-between items-start mb-1.5">
                                                        <div className="font-bold text-slate-700">{h.condition_name}</div>
                                                        {h.is_chronic && <span className="bg-amber-50 text-amber-600 border border-amber-100 text-[10px] px-2 py-0.5 rounded-full uppercase font-bold tracking-wide">Chronic</span>}
                                                    </div>
                                                    <div className="text-sm text-slate-500">{h.notes}</div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : <div className="text-slate-400 italic text-sm p-8 text-center bg-slate-50/30">No history records found.</div>}
                                </CardContent>
                            </Card>

                            {/* Vitals Form Area */}
                            <div className="lg:col-span-2">
                                <VisitForm patientId={patient.patient_id} />
                            </div>
                        </div>
                    </div>
                )}
            </main>
        </div>
    )
}
