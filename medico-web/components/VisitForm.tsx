'use client'
import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { api } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { Activity } from 'lucide-react'

export default function VisitForm({ patientId }: { patientId: number }) {
    const router = useRouter()
    const [loading, setLoading] = useState(false)
    const [complaint, setComplaint] = useState('')
    // Changed to strings to allow empty input without forcing 0
    const [vitals, setVitals] = useState({ sys: '120', dia: '80', hr: '80', temp: '98.6' })
    const [symptom, setSymptom] = useState({ name: '', sev: 3, dur: '' })
    const [symptoms, setSymptoms] = useState<any[]>([])

    async function handleSubmit() {
        setLoading(true)
        try {
            const payload = {
                patient_id: patientId,
                chief_complaint: complaint,
                bp_systolic: Number(vitals.sys), bp_diastolic: Number(vitals.dia),
                heart_rate: Number(vitals.hr), temperature: Number(vitals.temp),
                symptoms: symptoms.map(s => ({ symptom_name: s.name, severity_score: s.sev, duration: s.dur }))
            }
            await api.post('/patient-visits', payload)
            router.push('/queue')
        } catch (e: any) {
            console.error("Submission Error:", e)
            alert(`Error submitting triage: ${e.response?.data?.detail || e.message}`)
        } finally {
            setLoading(false)
        }
    }

    // Helper to handle numeric inputs gracefully
    const handleVitalChange = (field: string, value: string) => {
        setVitals(prev => ({ ...prev, [field]: value }))
    }

    return (
        <Card className="border-0 shadow-xl shadow-slate-200/50 rounded-2xl overflow-hidden bg-white h-full flex flex-col">
            <div className="h-1.5 bg-gradient-to-r from-blue-500 to-indigo-600 w-full"></div>
            <CardHeader className="bg-slate-50/50 border-b border-slate-100 pb-6 pt-8 px-8">
                <CardTitle className="text-xl font-bold text-slate-800 flex items-center gap-2">
                    <Activity className="text-blue-600" size={24} />
                    Clinical Assessment
                </CardTitle>
                <CardDescription className="text-slate-500 font-medium">Record vital signs and presenting symptoms.</CardDescription>
            </CardHeader>
            <CardContent className="p-8 space-y-8 flex-1">
                {/* Chief Complaint */}
                <div className="space-y-3">
                    <label className="text-sm font-bold text-slate-700 uppercase tracking-wide">Chief Complaint</label>
                    <Input
                        className="h-14 text-lg bg-white border-slate-200 focus:border-blue-500 shadow-sm rounded-xl"
                        value={complaint}
                        onChange={e => setComplaint(e.target.value)}
                        placeholder="e.g. Severe chest pain radiating to left arm..."
                    />
                </div>

                {/* Vitals Grid */}
                <div className="bg-slate-50/80 p-6 rounded-2xl border border-slate-200/60 space-y-4">
                    <div className="flex items-center gap-2 text-sm font-bold text-slate-500 uppercase tracking-widest mb-2">
                        <Activity size={14} /> Vital Signs
                    </div>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-400">Systolic (mmHg)</label>
                            <Input type="number" value={vitals.sys} onChange={e => handleVitalChange('sys', e.target.value)} className="font-mono text-lg font-bold text-slate-700 bg-white border-slate-200 h-12" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-400">Diastolic (mmHg)</label>
                            <Input type="number" value={vitals.dia} onChange={e => handleVitalChange('dia', e.target.value)} className="font-mono text-lg font-bold text-slate-700 bg-white border-slate-200 h-12" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-400">Heart Rate (BPM)</label>
                            <Input type="number" value={vitals.hr} onChange={e => handleVitalChange('hr', e.target.value)} className="font-mono text-lg font-bold text-red-500 bg-red-50/50 border-red-100 focus:border-red-300 h-12" />
                        </div>
                        <div className="space-y-1">
                            <label className="text-xs font-bold text-slate-400">Temp (°F)</label>
                            <Input type="number" step="0.1" value={vitals.temp} onChange={e => handleVitalChange('temp', e.target.value)} className="font-mono text-lg font-bold text-slate-700 bg-white border-slate-200 h-12" />
                        </div>
                    </div>
                </div>

                {/* Symptoms */}
                <div className="space-y-4">
                    <div className="flex justify-between items-end">
                        <label className="text-sm font-bold text-slate-700 uppercase tracking-wide">Symptoms Observed</label>
                        <span className="text-xs font-semibold text-slate-400">{symptoms.length} Recorded</span>
                    </div>

                    <div className="space-y-3 bg-slate-50/50 p-4 rounded-xl border border-slate-100 min-h-[100px]">
                        {symptoms.length === 0 && (
                            <div className="text-center py-6 text-slate-400 italic text-sm">No symptoms added yet.</div>
                        )}
                        {symptoms.map((s, i) => (
                            <div key={i} className="flex justify-between items-center bg-white p-3 px-4 rounded-lg border border-slate-200 shadow-sm animate-in fade-in slide-in-from-right-2">
                                <span className="font-medium text-slate-700 flex items-center gap-2">
                                    {s.name}
                                    <span className="text-slate-400 text-xs font-normal">({s.dur})</span>
                                </span>
                                <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${s.sev >= 4 ? 'bg-red-50 text-red-600 border border-red-100' : 'bg-emerald-50 text-emerald-600 border border-emerald-100'}`}>
                                    Severity: {s.sev}
                                </span>
                            </div>
                        ))}
                    </div>

                    <div className="grid grid-cols-12 gap-3 items-end">
                        <div className="col-span-5 space-y-1">
                            <Input placeholder="Symptom Name" className="bg-white" value={symptom.name} onChange={e => setSymptom({ ...symptom, name: e.target.value })} />
                            <label className="text-[10px] text-slate-400 pl-1 uppercase font-bold">Name</label>
                        </div>
                        <div className="col-span-2 space-y-1">
                            <Input type="number" min="1" max="5" className="bg-white text-center font-bold" value={symptom.sev} onChange={e => setSymptom({ ...symptom, sev: +e.target.value })} />
                            <label className="text-[10px] text-slate-400 pl-1 uppercase font-bold">Sev (1-5)</label>
                        </div>
                        <div className="col-span-3 space-y-1">
                            <Input placeholder="e.g. 2 days" className="bg-white" value={symptom.dur} onChange={e => setSymptom({ ...symptom, dur: e.target.value })} />
                            <label className="text-[10px] text-slate-400 pl-1 uppercase font-bold">Duration</label>
                        </div>
                        <div className="col-span-2 pb-5">
                            <Button size="sm" className="w-full bg-slate-900 text-white hover:bg-slate-800 font-bold" onClick={() => {
                                if (!symptom.name) return;
                                setSymptoms([...symptoms, symptom]);
                                setSymptom({ ...symptom, name: '', sev: 3, dur: '' });
                            }}>+</Button>
                        </div>
                    </div>
                </div>

                <div className="pt-4">
                    <Button
                        onClick={handleSubmit}
                        disabled={loading || !complaint}
                        className="w-full h-14 text-lg font-bold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-xl shadow-blue-200 hover:shadow-2xl hover:-translate-y-0.5 transition-all rounded-xl"
                    >
                        {loading ? "Processing Triage..." : "Submit Assessment & Calculate Risk"}
                    </Button>
                </div>
            </CardContent>
        </Card>
    )
}
