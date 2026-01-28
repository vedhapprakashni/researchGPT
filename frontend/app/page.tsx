'use client';

import { useState, useEffect } from 'react';
import { PaperSidebar } from './components/PaperSidebar';
import { ChatInterface } from './components/ChatInterface';
import { Header } from './components/Header';

export interface Paper {
  paper_id: string;
  filename: string;
  title?: string;
  upload_date: string;
  total_pages: number;
  total_chunks: number;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  mode?: string;
  timestamp: Date;
}

export interface Citation {
  paper_id: string;
  page: number;
  section: string;
  chunk_preview: string;
}

export interface PaperGroup {
  group_id: string;
  name: string;
  description?: string;
  paper_ids: string[];
  created_date: string;
}

export default function Home() {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [selectedPaper, setSelectedPaper] = useState<Paper | null>(null);
  const [groups, setGroups] = useState<PaperGroup[]>([]);
  const [selectedGroup, setSelectedGroup] = useState<PaperGroup | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<'academic' | 'simple' | 'eli5'>('academic');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  // API Base URL - uses environment variable in production, localhost in development
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

  // Fetch papers and groups on mount
  useEffect(() => {
    fetchPapers();
    fetchGroups();
  }, []);

  const fetchPapers = async () => {
    try {
      const res = await fetch(`${API_BASE}/list_papers`);
      if (!res.ok) return;
      const data = await res.json();
      setPapers(data.papers || []);
    } catch (error) {
      console.error('Failed to fetch papers:', error);
    }
  };

  const fetchGroups = async () => {
    try {
      const res = await fetch(`${API_BASE}/groups`);
      if (!res.ok) return;
      const data = await res.json();
      setGroups(data.groups || []);
    } catch (error) {
      console.error('Failed to fetch groups:', error);
    }
  };

  const createGroup = async (name: string, description?: string, paperIds: string[] = []) => {
    try {
      const res = await fetch(`${API_BASE}/groups`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, paper_ids: paperIds }),
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Failed to create group');
      }

      await fetchGroups();
      return { success: true };
    } catch (error: any) {
      console.error('Failed to create group:', error);
      return { success: false, error: error.message };
    }
  };

  const deleteGroup = async (groupId: string) => {
    try {
      const res = await fetch(`${API_BASE}/groups/${groupId}`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        console.error('Delete group failed with status:', res.status);
        return;
      }

      await fetchGroups();
      if (selectedGroup?.group_id === groupId) {
        setSelectedGroup(null);
      }
    } catch (error) {
      console.error('Delete group failed:', error);
    }
  };

  const addPapersToGroup = async (groupId: string, paperIds: string[]) => {
    try {
      const res = await fetch(`${API_BASE}/groups/${groupId}/papers`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(paperIds),
      });

      if (!res.ok) {
        throw new Error('Failed to add papers to group');
      }

      await fetchGroups();
      return { success: true };
    } catch (error: any) {
      console.error('Failed to add papers to group:', error);
      return { success: false, error: error.message };
    }
  };

  const uploadPaper = async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);

    try {
      setIsLoading(true);
      const res = await fetch(`${API_BASE}/upload_paper`, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || 'Upload failed');
      }

      await fetchPapers();
      return { success: true };
    } catch (error: any) {
      console.error('Upload failed:', error);
      return { success: false, error: error.message };
    } finally {
      setIsLoading(false);
    }
  };

  const deletePaper = async (paperId: string) => {
    try {
      const res = await fetch(`${API_BASE}/delete_paper/${paperId}`, {
        method: 'DELETE',
      });

      if (!res.ok) {
        console.error('Delete failed with status:', res.status);
        return;
      }

      await fetchPapers();
      if (selectedPaper?.paper_id === paperId) {
        setSelectedPaper(null);
      }
    } catch (error) {
      console.error('Delete failed:', error);
    }
  };

  const askQuestion = async (question: string) => {
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // If group_id is provided, get papers from group
      let paper_ids = null;
      if (selectedGroup) {
        paper_ids = selectedGroup.paper_ids;
      }

      const res = await fetch(`${API_BASE}/ask_question`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question,
          paper_id: selectedPaper?.paper_id || null,
          group_id: selectedGroup?.group_id || null,
          mode,
          top_k: 5,
        }),
      });

      if (!res.ok) {
        throw new Error('Failed to get answer');
      }

      const data = await res.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        mode: data.mode,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Question failed:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your question. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[rgb(var(--bg-primary))] flex flex-col">
      <Header
        mode={mode}
        setMode={setMode}
        toggleSidebar={() => setSidebarOpen(!sidebarOpen)}
      />

      <div className="flex flex-1 overflow-hidden">
        <PaperSidebar
          papers={papers}
          selectedPaper={selectedPaper}
          onSelectPaper={(paper) => {
            setSelectedPaper(paper);
            setSelectedGroup(null);
          }}
          onUpload={uploadPaper}
          onDelete={deletePaper}
          groups={groups}
          selectedGroup={selectedGroup}
          onSelectGroup={(group) => {
            setSelectedGroup(group);
            setSelectedPaper(null);
          }}
          onCreateGroup={createGroup}
          onDeleteGroup={deleteGroup}
          onAddPapersToGroup={addPapersToGroup}
          isOpen={sidebarOpen}
        />

        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          onSendMessage={askQuestion}
          selectedPaper={selectedPaper}
          selectedGroup={selectedGroup}
          mode={mode}
        />
      </div>
    </div>
  );
}
