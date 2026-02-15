'use client'

import { Activity, Stethoscope, Search, LayoutDashboard, Users, UserPlus } from 'lucide-react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'

export default function Header() {
    const pathname = usePathname()

    const links = [
        { href: '/', label: 'Dashboard', icon: LayoutDashboard },
        { href: '/triage', label: 'Triage', icon: UserPlus },
        { href: '/queue', label: 'Queues', icon: Users },
    ]

    return (
        <header className="border-b bg-white">
            <div className="flex h-16 items-center px-4 md:px-6">
                <Link href="/" className="flex items-center gap-2 font-bold text-xl text-blue-800 mr-8">
                    <div className="bg-blue-600 p-1.5 rounded-lg text-white">
                        <Stethoscope size={24} />
                    </div>
                    <span>Medico</span>
                </Link>

                <nav className="flex items-center gap-6">
                    {links.map((link) => {
                        const Icon = link.icon
                        const active = pathname === link.href
                        return (
                            <Link
                                key={link.href}
                                href={link.href}
                                className={cn(
                                    "flex items-center gap-2 text-sm font-medium transition-colors hover:text-blue-600",
                                    active ? "text-blue-600 border-b-2 border-blue-600 h-16 pt-0.5" : "text-slate-500"
                                )}
                            >
                                <Icon size={18} />
                                {link.label}
                            </Link>
                        )
                    })}
                </nav>

                <div className="ml-auto flex items-center gap-4">
                    <div className="flex items-center gap-2 px-3 py-1 bg-red-50 text-red-700 rounded-full text-xs font-semibold border border-red-100">
                        <Activity size={14} className="animate-pulse" />
                        <span>ER Live</span>
                    </div>
                </div>
            </div>
        </header>
    )
}
