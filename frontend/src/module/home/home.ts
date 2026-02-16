import { Component, afterNextRender, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

// PrimeNG Components
import { ButtonModule } from 'primeng/button';
import { CardModule } from 'primeng/card';
import { TagModule } from 'primeng/tag';
import { AvatarModule } from 'primeng/avatar';
import { AvatarGroupModule } from 'primeng/avatargroup';
import { DividerModule } from 'primeng/divider';
import { TimelineModule } from 'primeng/timeline';
import { ChipModule } from 'primeng/chip';
import { InputTextModule } from 'primeng/inputtext';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { AnimateOnScrollModule } from 'primeng/animateonscroll';

interface TimelineStep {
  number?: string;
  icon?: string;
  stepIcon: string;
  title: string;
  description: string;
}

interface Feature {
  icon: string;
  title: string;
  description: string;
}

@Component({
  selector: 'app-home',
  imports: [
    CommonModule,
    FormsModule,
    ButtonModule,
    CardModule,
    TagModule,
    AvatarModule,
    AvatarGroupModule,
    DividerModule,
    TimelineModule,
    ChipModule,
    InputTextModule,
    IconFieldModule,
    InputIconModule,
    AnimateOnScrollModule,
  ],
  templateUrl: './home.html',
  styleUrl: './home.scss',
})
export class Home {
  timelineSteps: TimelineStep[] = [
    {
      number: '1',
      stepIcon: 'pi pi-user-plus',
      title: 'Create Your Profile',
      description: 'Upload your CV or import from LinkedIn. Our AI extracts your skills, experience, and career aspirations automatically.',
    },
    {
      number: '2',
      stepIcon: 'pi pi-microchip-ai',
      title: 'AI Deep Analysis',
      description: 'Our algorithm analyzes 50+ data points to understand not just what you\'ve done, but what you\'re capable of achieving.',
    },
    {
      number: '3',
      stepIcon: 'pi pi-bolt',
      title: 'Instant Matching',
      description: 'Get a curated list of opportunities ranked by compatibility. No more endless scrolling through irrelevant listings.',
    },
    {
      icon: 'pi pi-check',
      stepIcon: 'pi pi-send',
      title: 'Apply with Confidence',
      description: 'One-click applications with AI-tailored cover letters. Track your progress and get insights to improve.',
    },
  ];

  features: Feature[] = [
    {
      icon: 'pi pi-microchip-ai',
      title: 'AI-Powered Matching',
      description: 'Our neural network analyzes your profile against thousands of listings to find the perfect fit.',
    },
    {
      icon: 'pi pi-bell',
      title: 'Smart Alerts',
      description: 'Get notified instantly when a high-match opportunity appears. Never miss the perfect job.',
    },
    {
      icon: 'pi pi-shield',
      title: 'Privacy First',
      description: 'Your data stays yours. We never sell or share your personal information with anyone.',
    },
    {
      icon: 'pi pi-chart-line',
      title: 'Application Tracker',
      description: 'Monitor all your applications in one place. Get insights on response rates and optimize.',
    },
    {
      icon: 'pi pi-file-edit',
      title: 'Resume Builder',
      description: 'AI-powered suggestions to tailor your CV for each application automatically.',
    },
    {
      icon: 'pi pi-comments',
      title: 'Interview Prep',
      description: 'AI-generated practice questions based on the job description to help you prepare.',
    },
  ];

  companies: string[] = ['Google', 'Meta', 'Amazon', 'Microsoft', 'Apple'];
}
