'use client';

import { useState } from 'react';
import type { Paper, PaperGroup } from '../page';

interface GroupModalProps {
    isOpen: boolean;
    onClose: () => void;
    onCreateGroup: (name: string, description?: string, paperIds?: string[]) => Promise<{ success: boolean; error?: string }>;
    papers: Paper[];
    existingGroup?: PaperGroup | null;
}

export function GroupModal({
    isOpen,
    onClose,
    onCreateGroup,
    papers,
    existingGroup,
}: GroupModalProps) {
    const [name, setName] = useState(existingGroup?.name || '');
    const [description, setDescription] = useState(existingGroup?.description || '');
    const [selectedPaperIds, setSelectedPaperIds] = useState<string[]>(existingGroup?.paper_ids || []);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [error, setError] = useState('');

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError('');

        if (!name.trim()) {
            setError('Group name is required');
            return;
        }

        setIsSubmitting(true);
        const result = await onCreateGroup(name.trim(), description.trim() || undefined, selectedPaperIds);
        setIsSubmitting(false);

        if (result.success) {
            // Reset form and close
            setName('');
            setDescription('');
            setSelectedPaperIds([]);
            onClose();
        } else {
            setError(result.error || 'Failed to create group');
        }
    };

    const togglePaper = (paperId: string) => {
        setSelectedPaperIds(prev =>
            prev.includes(paperId)
                ? prev.filter(id => id !== paperId)
                : [...prev, paperId]
        );
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 animate-fade-in">
            <div className="bg-[rgb(var(--bg-card))] border-2 border-[rgb(var(--border-hover))] max-w-lg w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col rounded-xl">
                {/* Header */}
                <div className="px-6 py-4 border-b border-[rgb(var(--border-subtle))]">
                    <h2 className="text-xl font-semibold text-[rgb(var(--galaxy-white))]">
                        {existingGroup ? 'Edit Group' : 'Create Paper Group'}
                    </h2>
                </div>

                {/* Form */}
                <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto">
                    <div className="p-6 space-y-4">
                        {/* Group Name */}
                        <div>
                            <label className="block text-sm font-medium text-[rgb(var(--galaxy-silver))] mb-2">
                                Group Name *
                            </label>
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                placeholder="e.g., Seizure Detection Papers"
                                className="w-full px-3 py-2 bg-[rgb(var(--bg-secondary))] border border-[rgb(var(--border-subtle))] rounded-lg text-[rgb(var(--galaxy-white))] placeholder:text-[rgb(var(--text-muted))] outline-none focus:border-[rgb(var(--accent-primary))]"
                                maxLength={100}
                            />
                        </div>

                        {/* Description */}
                        <div>
                            <label className="block text-sm font-medium text-[rgb(var(--galaxy-silver))] mb-2">
                                Description (optional)
                            </label>
                            <textarea
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder="What is this group about?"
                                rows={3}
                                className="w-full px-3 py-2 bg-[rgb(var(--bg-secondary))] border border-[rgb(var(--border-subtle))] rounded-lg text-[rgb(var(--galaxy-white))] placeholder:text-[rgb(var(--text-muted))] outline-none focus:border-[rgb(var(--accent-primary))] resize-none"
                                maxLength={500}
                            />
                        </div>

                        {/* Paper Selection */}
                        <div>
                            <label className="block text-sm font-medium text-[rgb(var(--galaxy-silver))] mb-2">
                                Select Papers ({selectedPaperIds.length} selected)
                            </label>

                            {papers.length === 0 ? (
                                <p className="text-sm text-[rgb(var(--text-muted))] py-4">
                                    No papers uploaded yet. Upload papers first to add them to a group.
                                </p>
                            ) : (
                                <div className="space-y-2 max-h-48 overflow-y-auto border border-[rgb(var(--border-subtle))] rounded-lg p-3">
                                    {papers.map((paper) => (
                                        <label
                                            key={paper.paper_id}
                                            className="flex items-start gap-3 cursor-pointer hover:bg-[rgb(var(--bg-tertiary))] p-2 rounded-lg smooth"
                                        >
                                            <input
                                                type="checkbox"
                                                checked={selectedPaperIds.includes(paper.paper_id)}
                                                onChange={() => togglePaper(paper.paper_id)}
                                                className="mt-1 w-4 h-4 accent-[rgb(var(--accent-primary))]"
                                            />
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm text-[rgb(var(--galaxy-white))] truncate">
                                                    {paper.title || paper.filename}
                                                </p>
                                                <p className="text-xs text-[rgb(var(--text-muted))]">
                                                    {paper.total_pages} pages • {paper.total_chunks} chunks
                                                </p>
                                            </div>
                                        </label>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Error Message */}
                        {error && (
                            <div className="px-3 py-2 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
                                {error}
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="px-6 py-4 border-t border-[rgb(var(--border-subtle))] flex justify-end gap-3">
                        <button
                            type="button"
                            onClick={onClose}
                            className="px-4 py-2 text-[rgb(var(--galaxy-silver))] hover:text-[rgb(var(--galaxy-white))] smooth"
                            disabled={isSubmitting}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={isSubmitting || !name.trim()}
                            className="px-6 py-2 rounded-lg bg-[rgb(var(--accent-primary))] text-white hover:shadow-[0_0_20px_rgba(130,140,255,0.5)] disabled:opacity-40 disabled:cursor-not-allowed smooth"
                        >
                            {isSubmitting ? 'Creating...' : existingGroup ? 'Save Changes' : 'Create Group'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
