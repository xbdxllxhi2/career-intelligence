import { Injectable } from '@angular/core';
import { Observable, of, delay } from 'rxjs';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  isStreaming?: boolean;
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

@Injectable({
  providedIn: 'root'
})
export class CareerChatService {
  private sessions: ChatSession[] = [];
  private currentSessionId: string | null = null;

  // Mock responses for career guidance
  private mockResponses: { [key: string]: string } = {
    resume: `Great question about your resume! Here are some key tips:

**1. Tailor it to the job**
Customize your resume for each position by highlighting relevant skills and experiences that match the job description.

**2. Quantify your achievements**
Instead of "Improved sales," say "Increased sales by 35% over 6 months." Numbers make your impact concrete.

**3. Keep it concise**
For most candidates, a one-page resume is ideal. Senior professionals can extend to two pages.

**4. Use strong action verbs**
Start bullet points with words like "Led," "Developed," "Implemented," "Achieved."

Would you like me to review your current resume or help you structure a specific section?`,

    interview: `Interview preparation is crucial! Here's my guidance:

**Before the Interview:**
- Research the company thoroughly (culture, recent news, products)
- Prepare stories using the STAR method (Situation, Task, Action, Result)
- Practice common questions out loud

**Common Questions to Prepare:**
1. "Tell me about yourself" - Have a 2-minute pitch ready
2. "Why this company?" - Show you've done your research
3. "What's your greatest weakness?" - Be honest but show growth

**During the Interview:**
- Ask thoughtful questions about the role and team
- Listen carefully before responding
- It's okay to take a moment to think

What specific type of interview are you preparing for? Technical, behavioral, or both?`,

    skills: `Let's talk about building your skills! 📚

**In-Demand Skills for 2026:**
- AI/ML fundamentals
- Cloud computing (AWS, Azure, GCP)
- Data analysis and visualization
- Communication and collaboration
- Project management

**How to Build Skills:**
1. **Online courses** - Coursera, Udemy, LinkedIn Learning
2. **Projects** - Build something real to demonstrate your abilities
3. **Certifications** - Industry-recognized credentials add credibility
4. **Open source** - Contribute to projects on GitHub

**Pro tip:** Focus on T-shaped skills - deep expertise in one area with broad knowledge across related fields.

What field are you most interested in developing skills for?`,

    salary: `Salary negotiation can feel intimidating, but you've got this! 💪

**Research First:**
- Use Glassdoor, Levels.fyi, LinkedIn Salary to find market rates
- Consider location, company size, and your experience level

**Negotiation Tips:**
1. **Never give the first number** if you can avoid it
2. **Consider total compensation** - base, bonus, equity, benefits
3. **Be confident but collaborative** - "Based on my research and experience..."
4. **Get it in writing** before accepting

**When to negotiate:**
- After receiving an offer, not during early interviews
- If the offer is below market rate
- When you have competing offers

What's your specific situation? New job offer or raise at current company?`,

    default: `I'm here to help with your career journey! 🚀

I can assist you with:
- **Resume & CV optimization**
- **Interview preparation** and common questions
- **Skill development** recommendations
- **Salary negotiation** strategies
- **Career path planning**
- **Job search strategies**
- **Networking tips**

Just ask me anything about your career, and I'll provide personalized guidance based on your situation.

What would you like to explore today?`
  };

  constructor() {
    this.loadSessions();
  }

  private loadSessions(): void {
    const saved = localStorage.getItem('careerChatSessions');
    if (saved) {
      this.sessions = JSON.parse(saved);
    }
  }

  private saveSessions(): void {
    localStorage.setItem('careerChatSessions', JSON.stringify(this.sessions));
  }

  getSessions(): ChatSession[] {
    return this.sessions.sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    );
  }

  getCurrentSession(): ChatSession | null {
    if (!this.currentSessionId) return null;
    return this.sessions.find(s => s.id === this.currentSessionId) || null;
  }

  createSession(): ChatSession {
    const session: ChatSession = {
      id: crypto.randomUUID(),
      title: 'New Chat',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date()
    };
    this.sessions.unshift(session);
    this.currentSessionId = session.id;
    this.saveSessions();
    return session;
  }

  setCurrentSession(sessionId: string): void {
    this.currentSessionId = sessionId;
  }

  deleteSession(sessionId: string): void {
    this.sessions = this.sessions.filter(s => s.id !== sessionId);
    if (this.currentSessionId === sessionId) {
      this.currentSessionId = this.sessions[0]?.id || null;
    }
    this.saveSessions();
  }

  sendMessage(content: string): Observable<ChatMessage> {
    if (!this.currentSessionId) {
      this.createSession();
    }

    const session = this.getCurrentSession()!;

    // Add user message
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      timestamp: new Date()
    };
    session.messages.push(userMessage);

    // Update session title from first message
    if (session.messages.length === 1) {
      session.title = content.slice(0, 50) + (content.length > 50 ? '...' : '');
    }

    session.updatedAt = new Date();
    this.saveSessions();

    // Generate mock response
    const response = this.generateMockResponse(content);

    // Simulate API delay
    return of(response).pipe(delay(800 + Math.random() * 1200));
  }

  addAssistantMessage(message: ChatMessage): void {
    const session = this.getCurrentSession();
    if (session) {
      session.messages.push(message);
      session.updatedAt = new Date();
      this.saveSessions();
    }
  }

  private generateMockResponse(userMessage: string): ChatMessage {
    const lowerMessage = userMessage.toLowerCase();
    let responseContent = this.mockResponses['default'];

    if (lowerMessage.includes('resume') || lowerMessage.includes('cv')) {
      responseContent = this.mockResponses['resume'];
    } else if (lowerMessage.includes('interview')) {
      responseContent = this.mockResponses['interview'];
    } else if (lowerMessage.includes('skill') || lowerMessage.includes('learn')) {
      responseContent = this.mockResponses['skills'];
    } else if (lowerMessage.includes('salary') || lowerMessage.includes('negotiat') || lowerMessage.includes('offer')) {
      responseContent = this.mockResponses['salary'];
    }

    return {
      id: crypto.randomUUID(),
      role: 'assistant',
      content: responseContent,
      timestamp: new Date()
    };
  }
}
