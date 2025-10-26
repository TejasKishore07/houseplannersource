import os
from typing import Optional
from datetime import datetime

import google.generativeai as genai


class HousePlanningAgent:
    """Minimal Gemini-backed AI assistant for house planning Q&A."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.api_key = gemini_api_key or os.getenv('GEMINI_API_KEY')
        self.model = None
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = self._init_model()
            except Exception:
                self.model = None

    def _init_model(self):
        """Prefer Gemini 2.0 Flash; fall back to stable 1.5 variants."""
        for name in (
            'gemini-2.0-flash',
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro-latest',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
        ):
            try:
                return genai.GenerativeModel(name)
            except Exception:
                continue
        return None
    
    def ask_ai(self, question: str, context: str = "") -> str:
        """Return a concise, practical answer. Falls back if model unavailable."""
        if not question or not isinstance(question, str):
            return "Please ask a clear question about your house plan."

        if not self.model:
            return self._fallback_answer(question)
        
        prompt = f"""
You are a professional yet friendly house and land planning advisor.  
- Answer queries on house design, land usage, construction, and cost estimation.  
- Respond in a natural, human-like style with clear headings: Design, Layout, Cost.  
- Use practical details (₹ per sq ft, room sizes, land usage, total cost range).  
- Keep answers crisp, 1–2 lines per section, easy to read, and natural.  
- Do not use **, #, *, or any bullet/markdown symbols in the answer.  
            
            Context: {context}
            Question: {question}
"""





        last_error = None
        for _ in range(2):
            try:
                res = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': 0.6,
                        'max_output_tokens': 512,
                    },
                )
                text = (res.text or '').strip()
                return text or self._fallback_answer(question)
            except Exception as e:
                last_error = str(e)
                continue

        return f"AI unavailable: {last_error}. {self._fallback_answer(question)}"

    # -------------------------
    # Internal helpers
    # -------------------------
    def _fallback_answer(self, question: str) -> str:
        q = (question or '').lower()
        if any(k in q for k in ('cost', 'price', 'estimat')):
            return 'Typical build cost ranges ₹1,200–2,000/sq ft based on materials and finish.'
        if 'orientation' in q or 'facing' in q:
            return 'Prefer East/North facing for light; shade West walls and buffer harsh South sun.'
        if 'size' in q or 'room' in q:
            return 'Good sizes: Master 12×14 ft, Bedroom 10×12 ft, Living 16×20 ft, Kitchen 10×12 ft.'
        if 'budget' in q:
            return 'Allocate ~60% build, 20% materials, 15% labour, 5% approvals; keep 10% buffer.'
        return 'I can help with costs, sizes, orientation and materials. Ask a specific question.'


