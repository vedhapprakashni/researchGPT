"""
PDF Parser Service
Extracts text from PDFs with section detection and page tracking
"""
import fitz  # PyMuPDF
import re
from typing import List, Dict, Tuple
from pathlib import Path


# Common section headers in research papers
SECTION_PATTERNS = [
    r'^abstract\s*$',
    r'^introduction\s*$',
    r'^related\s*work\s*$',
    r'^background\s*$',
    r'^methodology\s*$',
    r'^method[s]?\s*$',
    r'^approach\s*$',
    r'^proposed\s*(method|approach|system)\s*$',
    r'^experiment[s]?\s*$',
    r'^result[s]?\s*$',
    r'^evaluation\s*$',
    r'^discussion\s*$',
    r'^conclusion[s]?\s*$',
    r'^future\s*work\s*$',
    r'^reference[s]?\s*$',
    r'^acknowledge?ment[s]?\s*$',
    r'^appendix\s*',
    r'^\d+\.?\s*(introduction|related|background|method|result|conclusion)',
]


class PDFParser:
    """Parse PDF documents and extract structured text"""
    #converts all section patters to regex objects
    def __init__(self):
        self.section_patterns = [re.compile(p, re.IGNORECASE) for p in SECTION_PATTERNS]
    
    def parse(self, pdf_path: str) -> Dict:
        """
        Parse a PDF file and extract text with metadata
        
        Returns:
            Dict with:
                - pages: List of (page_num, text, detected_sections)
                - total_pages: int
                - title: str (extracted from first page)
        """
        doc = fitz.open(pdf_path)
        pages_data = []
        title = None
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            
            # Extract title from first page (usually largest font)
            if page_num == 0 and not title:
                title = self._extract_title(page)
            
            # Detect sections in this page
            sections = self._detect_sections(text)
            
            pages_data.append({
                "page_num": page_num + 1,  # 1-indexed
                "text": text.strip(),
                "sections": sections
            })
        
        doc.close()
        
        return {
            "pages": pages_data,
            "total_pages": len(pages_data),
            "title": title or Path(pdf_path).stem
        }
    
    def _extract_title(self, page) -> str:
        """Extract title from first page using font size heuristic"""
        blocks = page.get_text("dict")["blocks"]
        title_candidates = []
        
        for block in blocks:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                for span in line["spans"]:
                    # Larger fonts typically indicate titles
                    if span["size"] > 14:
                        title_candidates.append((span["size"], span["text"].strip()))
        
        if title_candidates:
            # Get the largest font text
            title_candidates.sort(key=lambda x: x[0], reverse=True)
            return title_candidates[0][1][:200]  # Limit title length
        
        return None
    
    def _detect_sections(self, text: str) -> List[Tuple[int, str]]:
        """
        Detect section headers in text
        
        Returns:
            List of (char_position, section_name)
        """
        sections = []
        lines = text.split('\n')
        char_pos = 0
        
        for line in lines:
            stripped = line.strip()
            if len(stripped) < 50:  # Section headers are usually short
                for pattern in self.section_patterns:
                    if pattern.match(stripped):
                        # Clean up section name
                        section_name = re.sub(r'^\d+\.?\s*', '', stripped)
                        section_name = section_name.title()
                        sections.append((char_pos, section_name))
                        break
            char_pos += len(line) + 1  # +1 for newline
        
        return sections
    
    def extract_text_by_section(self, pdf_path: str) -> List[Dict]:
        """
        Parse PDF and organize text by detected sections
        
        Returns:
            List of dicts with section, text, start_page, end_page
        """
        parsed = self.parse(pdf_path)
        
        # Build a flat list of all text with page and section info
        all_chunks = []
        current_section = "Abstract"  # Default starting section
        
        for page_data in parsed["pages"]:
            page_num = page_data["page_num"]
            text = page_data["text"]
            sections = page_data["sections"]
            
            if not sections:
                # No sections detected on this page, use current section
                all_chunks.append({
                    "section": current_section,
                    "text": text,
                    "page": page_num
                })
            else:
                # Split text by sections
                sections_sorted = sorted(sections, key=lambda x: x[0])
                prev_pos = 0
                
                for i, (pos, section_name) in enumerate(sections_sorted):
                    # Add text before this section
                    if pos > prev_pos:
                        chunk_text = text[prev_pos:pos].strip()
                        if chunk_text:
                            all_chunks.append({
                                "section": current_section,
                                "text": chunk_text,
                                "page": page_num
                            })
                    
                    current_section = section_name
                    prev_pos = pos
                
                # Add remaining text after last section header
                if prev_pos < len(text):
                    chunk_text = text[prev_pos:].strip()
                    if chunk_text:
                        all_chunks.append({
                            "section": current_section,
                            "text": chunk_text,
                            "page": page_num
                        })
        
        return all_chunks, parsed["title"], parsed["total_pages"]
