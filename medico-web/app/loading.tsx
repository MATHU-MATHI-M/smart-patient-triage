export default function Loading() {
    return (
        <div className="flex h-screen w-full items-center justify-center bg-slate-50/50 backdrop-blur-sm z-50">
            <div className="relative flex flex-col items-center">
                {/* Pulse Rings */}
                <div className="absolute h-24 w-24 rounded-full border-4 border-blue-100 animate-[ping_1.5s_ease-in-out_infinite]"></div>
                <div className="absolute h-24 w-24 rounded-full border-4 border-blue-200 animate-[ping_1.5s_ease-in-out_infinite_200ms]"></div>

                {/* Center Spinner */}
                <div className="h-16 w-16 animate-spin rounded-full border-b-4 border-t-4 border-blue-600 shadow-lg shadow-blue-500/50"></div>

                <div className="mt-8 text-lg font-bold text-slate-600 animate-pulse">
                    Loading Medico...
                </div>
            </div>
        </div>
    )
}
