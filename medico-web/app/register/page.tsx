'use client'
import { useEffect } from 'react'
import { useRouter } from 'next/navigation'

export default function RegisterRedirect() {
    const router = useRouter()
    useEffect(() => {
        router.replace('/triage')
    }, [router])

    return (
        <div className="flex items-center justify-center min-h-screen bg-slate-50">
            <div className="animate-pulse flex flex-col items-center">
                <div className="h-8 w-8 bg-blue-600 rounded-full mb-4"></div>
                <p className="text-slate-500">Redirecting to Patient Registry...</p>
            </div>
        </div>
    )
}
