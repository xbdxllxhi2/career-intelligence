import { Component, Input } from '@angular/core';

import { TextareaModule } from 'primeng/textarea';
import { FormsModule } from '@angular/forms';
import { AccordionModule } from 'primeng/accordion';
import { SplitterModule } from 'primeng/splitter';
import { QuestionAnswer } from '../../models/interface/question-answer';
import { ButtonModule } from 'primeng/button';

@Component({
  selector: 'app-ai-chat',
  imports: [TextareaModule, FormsModule, AccordionModule, SplitterModule, ButtonModule],
  templateUrl: './ai-chat.html',
  styleUrl: './ai-chat.scss',
})
export class AiChat {
  textareaValue: string = '';
  @Input() conversation: QuestionAnswer[] = [];


  submitQuestion() {

  }

  isConversationEmpty(): boolean {
    return this.conversation.length === 0;
  }


  getConversation(): QuestionAnswer[] {
    return this.conversation;
  }

}

