import { Component } from '@angular/core';
import { TextareaModule } from 'primeng/textarea';
import { FormsModule } from '@angular/forms';
import { AccordionModule } from 'primeng/accordion';
import { SplitterModule } from 'primeng/splitter';
import { QuestionAnswer } from '../../models/interface/question-answer';
import { AiChat } from "../ai-chat/ai-chat";
import { JobResults } from "../job-results/job-results";
import { JobOffer } from '../../models/interface/job-offer';

@Component({
  selector: 'app-job-finder',
  imports: [TextareaModule, FormsModule, AccordionModule, SplitterModule, AiChat, JobResults],
  templateUrl: './job-finder.html',
  styleUrl: './job-finder.scss',
})
export class JobFinder {
  textareaValue: string = '';
  conversation: QuestionAnswer[] = [];
  showResults: boolean = true;
  resultsData: any[] = [];



  isConversationEmpty(): boolean {
    return false;
  }

  closeResult() {
    this.showResults = !this.showResults;
  }

  getJobOffers(): JobOffer[] {
   return [
    { 
    title: 'Backend Engineer', 
    company: 'Proxym Group', 
    location: 'Nouakchott', 
    description: 'lorem ipsum dolor sit amet consectetur adipiscing elit lorem ipsum dolor sit amet consectetur adipiscing elit lorem ipsum dolor sit amet consectetur adipiscing elit', 
    logo: 'https://via.placeholder.com/40?text=P' 
  },
  { 
    title: 'Frontend Engineer', 
    company: 'Acme Inc', 
    location: 'Paris', 
    description: 'Work on Angular projects', 
    logo: 'https://via.placeholder.com/40?text=A' 
  },
  { 
    title: 'Full Stack Developer', 
    company: 'Tech Corp', 
    location: 'Remote', 
    description: 'Angular + Node.js', 
    logo: 'https://via.placeholder.com/40?text=T' 
  },
];

  }

  getConversation(): QuestionAnswer[] {
    return [
      {
        question: "What is the capital of France?",
        summary: "France's capital city is Paris.",
        reasoning: "Paris is the largest city in France and serves as the political, cultural, and economic center.",
        answer: "Paris"
      },
      {
        question: "How does photosynthesis work?",
        summary: "Photosynthesis converts sunlight into chemical energy.",
        reasoning: "Plants absorb sunlight using chlorophyll, which converts carbon dioxide and water into glucose and oxygen.",
        answer: "Photosynthesis is the process by which plants make food using sunlight, water, and carbon dioxide."
      },
      {
        question: "What are the benefits of regular exercise?",
        summary: "Exercise improves physical and mental health.",
        reasoning: "Regular activity strengthens muscles and bones, boosts cardiovascular health, and releases endorphins that improve mood.",
        answer: "Regular exercise enhances fitness, prevents diseases, and supports mental well-being."
      },
      {
        question: "Explain the theory of relativity in simple terms.",
        summary: "Einstein's theory explains how space, time, and gravity interact.",
        reasoning: "It shows that time and space are relative and affected by speed and mass, fundamentally changing our understanding of physics.",
        answer: "The theory of relativity describes how objects move and experience time differently depending on speed and gravity."
      },
      {
        question: "What is a blockchain?",
        summary: "Blockchain is a decentralized digital ledger.",
        reasoning: "It records transactions across multiple computers securely, preventing data tampering without a central authority.",
        answer: "A blockchain is a distributed database that maintains a secure and transparent record of digital transactions."
      }
    ];
  }

}
