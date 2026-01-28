'use client';

import { useState, useRef, useCallback } from 'react';
import type { Paper, PaperGroup } from '../page';
import { GroupModal } from './GroupModal';

interface PaperSidebarProps {
    papers: Paper[];
    selectedPaper: Paper | null;
    onSelectPaper: (paper: Paper | null) => void;
    onUpload: (file: File) => Promise<{ success: boolean; error?: string }>;
    onDelete: (paperId: string) => void;
    groups: PaperGroup[];
    selectedGroup: PaperGroup | null;
    onSelectGroup: (group: PaperGroup | null) => void;
    onCreateGroup: (name: string, description?: string, paperIds?: string[]) => Promise<{ success: boolean; error?: string }>;
    onDeleteGroup: (groupId: string) => void;
    onAddPapersToGroup: (groupId: string, paperIds: string[]) => Promise<{ success: boolean; error?: string }>;
    isOpen: boolean;
}

export function PaperSidebar({
    papers,
    selectedPaper,
    onSelectPaper,
    onUpload,
    onDelete,
    groups,
    selectedGroup,
    onSelectGroup,
    onCreateGroup,
    onDeleteGroup,
    onAddPapersToGroup,
    isOpen,
}: PaperSidebarProps) {
    const [isDragging, setIsDragging] = useState(false);
    const [uploadProgress, setUploadProgress] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [showGroupModal, setShowGroupModal] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleDragOver = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    }, []);

    const handleDragLeave = useCallback((e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    }, []);

    const handleDrop = useCallback(async (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        setError(null);

        const file = e.dataTransfer.files[0];
        if (file && file.type === 'application/pdf') {
            await handleFileUpload(file);
        } else {
            setError('Please upload a PDF file');
        }
    }, []);

    const handleFileUpload = async (file: File) => {
        setUploadProgress('Processing...');
        setError(null);

        const result = await onUpload(file);

        if (result.success) {
            setUploadProgress('✓ Success!');
            setTimeout(() => setUploadProgress(null), 2000);
        } else {
            setError(result.error || 'Upload failed');
            setUploadProgress(null);
        }
    };

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (file) {
            await handleFileUpload(file);
        }
    };

    return (
        <aside
            className={`glass border-r border-[rgb(var(--border-subtle))] flex flex-col smooth overflow-hidden ${isOpen ? 'w-72' : 'w-0'
                }`}
        >
            <div className="p-4 flex flex-col h-full min-w-[288px]">
                {/* Upload zone */}
                <div
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                    className={`dropzone rounded-xl p-5 text-center cursor-pointer mb-4 ${isDragging ? 'active' : ''
                        }`}
                >
                    <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileSelect}
                        accept=".pdf"
                        className="hidden"
                    />

                    <div className="w-10 h-10 mx-auto mb-3 rounded-full bg-[rgb(var(--bg-tertiary))] flex items-center justify-center">
                        <svg className="w-5 h-5 text-[rgb(var(--accent-primary))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                        </svg>
                    </div>

                    <p className="text-sm text-[rgb(var(--galaxy-silver))]">
                        {uploadProgress || 'Drop PDF or click to upload'}
                    </p>

                    {error && (
                        <p className="text-xs text-[rgb(var(--error))] mt-2">{error}</p>
                    )}
                </div>

                {/* Groups Section */}
                <div className="mb-4">
                    <div className="flex items-center justify-between mb-2 px-1">
                        <p className="text-xs font-medium text-[rgb(var(--text-muted))] uppercase tracking-wider">
                            Groups ({groups.length})
                        </p>
                        <button
                            onClick={() => setShowGroupModal(true)}
                            className="text-[rgb(var(--accent-primary))] hover:text-[rgb(var(--galaxy-white))] smooth"
                            title="Create new group"
                        >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                        </button>
                    </div>

                    {groups.length > 0 ? (
                        <div className="space-y-1 mb-3">
                            {groups.map((group) => (
                                <div
                                    key={group.group_id}
                                    onClick={() => onSelectGroup(group)}
                                    className={`relative group/item rounded-lg p-3 cursor-pointer smooth ${selectedGroup?.group_id === group.group_id
                                            ? 'bg-[rgb(var(--accent-primary))]/20 border border-[rgb(var(--accent-primary))]/40 text-[rgb(var(--galaxy-white))]'
                                            : 'hover:bg-[rgb(var(--bg-tertiary))] text-[rgb(var(--galaxy-silver))] border border-transparent'
                                        }`}
                                >
                                    <div className="flex items-start gap-2">
                                        <span className="text-base mt-0.5">📁</span>
                                        <div className="flex-1 min-w-0">
                                            <p className="font-medium text-sm truncate">
                                                {group.name}
                                            </p>
                                            <p className="text-xs text-[rgb(var(--text-muted))]">
                                                {group.paper_ids.length} papers
                                            </p>
                                        </div>
                                        <button
                                            onClick={(e) => {
                                                e.stopPropagation();
                                                if (confirm(`Delete group "${group.name}"? Papers will not be deleted.`)) {
                                                    onDeleteGroup(group.group_id);
                                                }
                                            }}
                                            className="opacity-0 group-hover/item:opacity-100 p-1 rounded hover:bg-[rgb(var(--error))]/20 smooth"
                                        >
                                            <svg className="w-3.5 h-3.5 text-[rgb(var(--error))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                            </svg>
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <p className="text-xs text-[rgb(var(--text-muted))] px-1 mb-3">
                            No groups yet
                        </p>
                    )}
                </div>

                {/* All papers option */}
                <button
                    onClick={() => onSelectPaper(null)}
                    className={`w-full text-left p-3 rounded-lg mb-3 smooth ${selectedPaper === null && selectedGroup === null
                        ? 'bg-[rgb(var(--accent-primary))]/20 border border-[rgb(var(--accent-primary))]/40 text-[rgb(var(--galaxy-white))]'
                        : 'hover:bg-[rgb(var(--bg-tertiary))] text-[rgb(var(--galaxy-silver))] border border-transparent'
                        }`}
                >
                    <div className="flex items-center gap-3">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                        </svg>
                        <span className="font-medium text-sm">All Papers</span>
                    </div>
                </button>

                {/* Paper list */}
                <div className="flex-1 overflow-y-auto space-y-2">
                    <p className="text-xs font-medium text-[rgb(var(--text-muted))] uppercase tracking-wider px-1 mb-2">
                        Library ({papers.length})
                    </p>

                    {papers.length === 0 ? (
                        <div className="text-center py-8 text-[rgb(var(--text-muted))]">
                            <svg className="w-10 h-10 mx-auto mb-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            <p className="text-sm">No papers yet</p>
                        </div>
                    ) : (
                        papers.map((paper) => (
                            <PaperCard
                                key={paper.paper_id}
                                paper={paper}
                                isSelected={selectedPaper?.paper_id === paper.paper_id}
                                onSelect={() => onSelectPaper(paper)}
                                onDelete={() => onDelete(paper.paper_id)}
                            />
                        ))
                    )}
                </div>
            </div>

            {/* Group Modal */}
            <GroupModal
                isOpen={showGroupModal}
                onClose={() => setShowGroupModal(false)}
                onCreateGroup={onCreateGroup}
                papers={papers}
            />
        </aside>
    );
}

function PaperCard({
    paper,
    isSelected,
    onSelect,
    onDelete,
}: {
    paper: Paper;
    isSelected: boolean;
    onSelect: () => void;
    onDelete: () => void;
}) {
    const [showDelete, setShowDelete] = useState(false);

    return (
        <div
            className={`relative group rounded-lg p-3 cursor-pointer smooth ${isSelected
                ? 'bg-[rgb(var(--accent-primary))]/15 border border-[rgb(var(--accent-primary))]/30'
                : 'hover:bg-[rgb(var(--bg-tertiary))] border border-transparent'
                }`}
            onClick={onSelect}
            onMouseEnter={() => setShowDelete(true)}
            onMouseLeave={() => setShowDelete(false)}
        >
            <div className="flex items-start gap-3">
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center shrink-0 ${isSelected ? 'bg-[rgb(var(--accent-primary))]/25' : 'bg-[rgb(var(--bg-tertiary))]'
                    }`}>
                    <svg className="w-4 h-4 text-[rgb(var(--accent-primary))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                </div>

                <div className="flex-1 min-w-0">
                    <p className="font-medium text-sm truncate text-[rgb(var(--galaxy-light))]">
                        {paper.title || paper.filename}
                    </p>
                    <p className="text-xs text-[rgb(var(--text-muted))] mt-0.5">
                        {paper.total_pages} pages
                    </p>
                </div>
            </div>

            {/* Delete button */}
            {showDelete && (
                <button
                    onClick={(e) => {
                        e.stopPropagation();
                        onDelete();
                    }}
                    className="absolute top-2 right-2 p-1.5 rounded-lg bg-[rgb(var(--error))]/20 hover:bg-[rgb(var(--error))]/40 smooth"
                >
                    <svg className="w-3.5 h-3.5 text-[rgb(var(--error))]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            )}
        </div>
    );
}
