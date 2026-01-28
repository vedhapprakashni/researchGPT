'use client';

import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import type { Message, Paper, Citation, PaperGroup } from '../page';

interface ChatInterfaceProps {
    messages: Message[];
    isLoading: boolean;
    onSendMessage: (message: string) => void;
    selectedPaper: Paper | null;
    selectedGroup: PaperGroup | null;
    mode: string;
}

export function ChatInterface({
    messages,
    isLoading,
    onSendMessage,
    selectedPaper,
    selectedGroup,
    mode,
}: ChatInterfaceProps) {
    const [input, setInput] = useState('');
    const messagesEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (input.trim() && !isLoading) {
            onSendMessage(input.trim());
            setInput('');
        }
    };

    // Show welcome state when no messages
    if (messages.length === 0) {
        return (
            <main className="flex-1 flex flex-col items-center justify-center min-w-0 bg-[rgb(var(--bg-primary))] p-8">
                <div className="max-w-2xl w-full text-center space-y-6">
                    <div className="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-[rgb(var(--accent-primary))] to-[rgb(var(--accent-secondary))] flex items-center justify-center glow">
                        <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                    </div>

                    <div>
                        <h1 className="text-3xl font-bold text-[rgb(var(--galaxy-white))] mb-2">
                            Ask about your research
                        </h1>
                        <p className="text-[rgb(var(--galaxy-silver))]">
                            {selectedGroup
                                ? `Querying ${selectedGroup.paper_ids.length} papers in "${selectedGroup.name}"`
                                : selectedPaper
                                    ? `Focused on: ${selectedPaper.title || selectedPaper.filename}`
                                    : 'Upload a paper or select a group to get started'}
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="relative">
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            placeholder="Ask a question about your papers..."
                            className="w-full px-6 py-4 bg-[rgb(var(--bg-secondary))] border-2 border-[rgb(var(--border-hover))] rounded-xl text-[rgb(var(--galaxy-white))] placeholder:text-[rgb(var(--text-muted))] focus:border-[rgb(var(--accent-primary))] text-lg"
                        />
                        <button
                            type="submit"
                            disabled={!input.trim() || isLoading}
                            className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-lg bg-[rgb(var(--accent-primary))] text-white hover:shadow-[0_0_20px_rgba(130,140,255,0.5)] disabled:opacity-40 smooth"
                        >
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                            </svg>
                        </button>
                    </form>
                </div>
            </main>
        );
    }

    // Chat mode - messages at top, input at bottom
    return (
        <main className="flex-1 flex flex-col min-w-0 bg-[rgb(var(--bg-primary))]">
            {/* Context indicator */}
            {(selectedPaper || selectedGroup) && (
                <div className="px-6 py-2.5 bg-[rgb(var(--accent-primary))]/5 border-b border-[rgb(var(--border-subtle))]">
                    <div className="flex items-center gap-2 text-sm">
                        <div className="w-2 h-2 rounded-full bg-[rgb(var(--accent-primary))] animate-pulse" />
                        <span className="text-[rgb(var(--galaxy-silver))]">Focused:</span>
                        {selectedGroup ? (
                            <span className="text-[rgb(var(--galaxy-light))] truncate">
                                📁 {selectedGroup.name} ({selectedGroup.paper_ids.length} papers)
                            </span>
                        ) : (
                            <span className="text-[rgb(var(--galaxy-light))] truncate">
                                {selectedPaper?.title || selectedPaper?.filename}
                            </span>
                        )}
                    </div>
                </div>
            )}

            {/* Messages area */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="max-w-4xl mx-auto space-y-6">
                    {messages.map((message) => (
                        <MessageBubble key={message.id} message={message} />
                    ))}

                    {isLoading && (
                        <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-[rgb(var(--accent-primary))]/20 flex items-center justify-center">
                                <div className="w-4 h-4 border-2 border-[rgb(var(--accent-primary))] border-t-transparent rounded-full animate-spin" />
                            </div>
                            <div className="flex-1 p-4 rounded-xl bg-[rgb(var(--bg-secondary))]">
                                <div className="loading-shimmer h-4 w-3/4 rounded mb-2" />
                                <div className="loading-shimmer h-4 w-1/2 rounded" />
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>
            </div>

            {/* Input area */}
            <div className="p-4 border-t border-[rgb(var(--border-subtle))]">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto flex gap-3">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a follow-up question..."
                        className="flex-1 px-4 py-3 bg-[rgb(var(--bg-secondary))] border border-[rgb(var(--border-subtle))] rounded-xl text-[rgb(var(--galaxy-white))] placeholder:text-[rgb(var(--text-muted))] focus:border-[rgb(var(--accent-primary))]"
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || isLoading}
                        className="px-6 py-3 rounded-xl bg-[rgb(var(--accent-primary))] text-white hover:shadow-[0_0_20px_rgba(130,140,255,0.5)] disabled:opacity-40 smooth"
                    >
                        Send
                    </button>
                </form>
            </div>
        </main>
    );
}

function MessageBubble({ message }: { message: Message }) {
    const isUser = message.role === 'user';

    return (
        <div className={`flex items-start gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${isUser
                    ? 'bg-[rgb(var(--accent-secondary))]/20'
                    : 'bg-[rgb(var(--accent-primary))]/20'
                }`}>
                {isUser ? (
                    <svg className="w-4 h-4 text-[rgb(var(--accent-secondary))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                ) : (
                    <svg className="w-4 h-4 text-[rgb(var(--accent-primary))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                )}
            </div>

            <div className={`flex-1 p-4 rounded-xl ${isUser
                    ? 'bg-[rgb(var(--accent-secondary))]/10 border border-[rgb(var(--accent-secondary))]/20'
                    : 'bg-[rgb(var(--bg-secondary))] border border-[rgb(var(--border-subtle))]'
                }`}>
                <div className="prose prose-invert prose-sm max-w-none">
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                </div>

                {message.citations && message.citations.length > 0 && (
                    <div className="mt-4 pt-4 border-t border-[rgb(var(--border-subtle))]">
                        <p className="text-xs font-medium text-[rgb(var(--galaxy-silver))] mb-2">Sources:</p>
                        <div className="space-y-2">
                            {message.citations.map((citation, idx) => (
                                <div key={idx} className="text-xs p-2 rounded bg-[rgb(var(--bg-tertiary))]">
                                    <span className="text-[rgb(var(--accent-primary))]">
                                        Page {citation.page}
                                    </span>
                                    <span className="text-[rgb(var(--text-muted))]"> • {citation.section}</span>
                                    <p className="mt-1 text-[rgb(var(--galaxy-silver))] line-clamp-2">
                                        {citation.chunk_preview}
                                    </p>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
