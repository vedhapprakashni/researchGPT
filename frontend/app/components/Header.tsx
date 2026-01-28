'use client';

interface HeaderProps {
    mode: 'academic' | 'simple' | 'eli5';
    setMode: (mode: 'academic' | 'simple' | 'eli5') => void;
    toggleSidebar: () => void;
}

export function Header({ mode, setMode, toggleSidebar }: HeaderProps) {
    const modes = [
        { id: 'academic', label: 'Academic', icon: '📚' },
        { id: 'simple', label: 'Simple', icon: '💡' },
        { id: 'eli5', label: 'ELI5', icon: '🧒' },
    ] as const;

    return (
        <header className="glass border-b border-[rgb(var(--border-subtle))] px-6 py-3">
            <div className="flex items-center justify-between">
                {/* Left: Menu and Logo */}
                <div className="flex items-center gap-4">
                    <button
                        onClick={toggleSidebar}
                        className="p-2 rounded-lg hover:bg-[rgb(var(--bg-tertiary))] smooth"
                    >
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>

                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[rgb(var(--accent-primary))] to-[rgb(var(--accent-secondary))] flex items-center justify-center">
                            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                        </div>
                        <span className="text-lg font-semibold">
                            Research<span className="gradient-text">GPT</span>
                        </span>
                    </div>
                </div>

                {/* Center: Mode Selector */}
                <div className="flex items-center gap-1 p-1 rounded-lg bg-[rgb(var(--bg-tertiary))]">
                    {modes.map((m) => (
                        <button
                            key={m.id}
                            onClick={() => setMode(m.id)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium smooth ${mode === m.id
                                    ? 'bg-[rgb(var(--accent-primary))] text-white shadow-lg'
                                    : 'text-[rgb(var(--galaxy-silver))] hover:text-[rgb(var(--galaxy-white))]'
                                }`}
                        >
                            <span>{m.icon}</span>
                            <span className="hidden sm:inline">{m.label}</span>
                        </button>
                    ))}
                </div>

                {/* Right: Placeholder */}
                <div className="w-20" />
            </div>
        </header>
    );
}
