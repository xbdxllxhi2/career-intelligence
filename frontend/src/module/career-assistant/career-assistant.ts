import { Component, inject, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ButtonModule } from 'primeng/button';
import { TooltipModule } from 'primeng/tooltip';
import { CareerChatService, ChatSession } from '../../service/career-chat.service';
import { KeycloakService } from 'keycloak-angular';
import { environment } from '../../environments/environments';
import { FormatMarkdownPipe } from '../../shared/pipes/format-markdown.pipe';
import { TranslocoModule, TranslocoService } from '@jsverse/transloco';

@Component({
  selector: 'app-career-assistant',
  standalone: true,
  imports: [CommonModule, FormsModule, ButtonModule, TooltipModule, FormatMarkdownPipe, TranslocoModule],
  templateUrl: './career-assistant.html',
  styleUrl: './career-assistant.scss'
})
export class CareerAssistant implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;
  @ViewChild('messageInput') private messageInput!: ElementRef;

  private chatService = inject(CareerChatService);
  private keycloak = inject(KeycloakService);
  private transloco = inject(TranslocoService);

  isAuthenticated = false;
  userName = '';
  userInitials = '';

  sessions: ChatSession[] = [];
  currentSession: ChatSession | null = null;
  messageText = '';
  isLoading = false;
  showSidebar = true;
  shouldScrollToBottom = false;

  suggestedPrompts = [
    { icon: 'pi-file-edit', textKey: 'assistant.prompts.resume', color: 'text-emerald-400' },
    { icon: 'pi-comments', textKey: 'assistant.prompts.interview', color: 'text-blue-400' },
    { icon: 'pi-chart-line', textKey: 'assistant.prompts.skills', color: 'text-amber-400' },
    { icon: 'pi-wallet', textKey: 'assistant.prompts.salary', color: 'text-purple-400' }
  ];

  ngOnInit(): void {
    this.initAuth();
    this.loadSessions();
  }

  ngAfterViewChecked(): void {
    if (this.shouldScrollToBottom) {
      this.scrollToBottom();
      this.shouldScrollToBottom = false;
    }
  }

  private initAuth(): void {
    if (environment.keycloak.enabled) {
      this.isAuthenticated = this.keycloak.isLoggedIn();
      if (this.isAuthenticated) {
        this.keycloak.loadUserProfile().then(profile => {
          this.userName = profile.firstName || profile.username || 'User';
          this.userInitials = this.getInitials(profile.firstName, profile.lastName);
        });
      }
    } else {
      this.isAuthenticated = true;
      this.userName = 'User';
      this.userInitials = 'U';
    }
  }

  private getInitials(firstName?: string, lastName?: string): string {
    const first = firstName?.charAt(0)?.toUpperCase() || '';
    const last = lastName?.charAt(0)?.toUpperCase() || '';
    return first + last || 'U';
  }

  private loadSessions(): void {
    this.sessions = this.chatService.getSessions();
    this.currentSession = this.chatService.getCurrentSession();
  }

  newChat(): void {
    this.currentSession = this.chatService.createSession();
    this.loadSessions();
    this.messageText = '';
  }

  selectSession(session: ChatSession): void {
    this.chatService.setCurrentSession(session.id);
    this.currentSession = session;
    this.shouldScrollToBottom = true;
  }

  deleteSession(event: Event, session: ChatSession): void {
    event.stopPropagation();
    this.chatService.deleteSession(session.id);
    this.loadSessions();
    this.currentSession = this.chatService.getCurrentSession();
  }

  sendMessage(text?: string): void {
    const content = text || this.messageText.trim();
    if (!content || this.isLoading) return;

    this.messageText = '';
    this.isLoading = true;
    this.shouldScrollToBottom = true;

    if (!this.currentSession) {
      this.currentSession = this.chatService.createSession();
      this.loadSessions();
    }

    this.chatService.sendMessage(content).subscribe({
      next: (response) => {
        this.chatService.addAssistantMessage(response);
        this.loadSessions();
        this.currentSession = this.chatService.getCurrentSession();
        this.isLoading = false;
        this.shouldScrollToBottom = true;
      },
      error: () => {
        this.isLoading = false;
      }
    });
  }

  usePrompt(prompt: string): void {
    const translatedPrompt = this.transloco.translate(prompt);
    this.sendMessage(translatedPrompt);
  }

  onKeydown(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  private scrollToBottom(): void {
    if (this.messagesContainer) {
      const el = this.messagesContainer.nativeElement;
      el.scrollTop = el.scrollHeight;
    }
  }

  toggleSidebar(): void {
    this.showSidebar = !this.showSidebar;
  }

  formatTime(date: Date): string {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  formatDate(date: Date): string {
    const d = new Date(date);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (d.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (d.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
    }
  }

  login(): void {
    this.keycloak.login({
      redirectUri: window.location.origin + '/assistant'
    });
  }
}
