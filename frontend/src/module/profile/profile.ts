import { Component, Input, OnInit } from '@angular/core';
import { TextareaModule } from 'primeng/textarea';
import {
  AbstractControl,
  FormArray,
  FormBuilder,
  FormGroup,
  FormsModule,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { AccordionModule } from 'primeng/accordion';
import { SplitterModule } from 'primeng/splitter';
import { QuestionAnswer } from '../../models/interface/question-answer';
import { ButtonModule } from 'primeng/button';
import { FileUploadModule } from 'primeng/fileupload';
import { InputGroupModule } from 'primeng/inputgroup';
import { InputGroupAddonModule } from 'primeng/inputgroupaddon';
import { IftaLabelModule } from 'primeng/iftalabel';
import { InplaceModule } from 'primeng/inplace';
import { UserProfile } from '../../models/interface/cv-profile';
import { SkeletonModule } from 'primeng/skeleton';
import { CommonModule } from '@angular/common';
import { DatePickerModule } from 'primeng/datepicker';
import { FloatLabelModule } from 'primeng/floatlabel';
import { ProfileService } from '../../service/profile-service';
import { ToastModule } from 'primeng/toast';
import { MessageService } from 'primeng/api';

@Component({
  selector: 'app-profile',
  imports: [
    ReactiveFormsModule,
    TextareaModule,
    AccordionModule,
    SplitterModule,
    ButtonModule,
    FileUploadModule,
    InputGroupModule,
    InputGroupAddonModule,
    IftaLabelModule,
    InplaceModule,
    SkeletonModule,
    CommonModule,
    DatePickerModule,
    FormsModule,
    FloatLabelModule,
    ToastModule,
  ],
  providers: [MessageService],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})
export class Profile {
  @Input() conversation: QuestionAnswer[] = [];

  profileData!: UserProfile;

  profileForm!: FormGroup;

  constructor(
    private fb: FormBuilder,
    private messageService: MessageService,
    private profileService: ProfileService,
  ) {}

  ngOnInit(): void {
    this.initForm();
    this.initProfileData();
  }

  private initProfileData(): void {
    this.profileService.getUserProfile().subscribe({
      next: (profile) => {
        console.log('Got Profile ', profile);
        this.profileData = profile;
        this.profileForm.patchValue(this.profileData);
        if (profile.experience?.length) {
          this.patchExperience(profile.experience);
        }

        if (profile.projects?.length) {
          this.patchProjects(profile.projects);
        }
      },
    });
  }

  private initForm(): void {
    this.profileForm = this.fb.nonNullable.group({
      firstName: [''],
      lastName: [''],
      title: [''],
      summary: [''],
      email: ['', [Validators.required, Validators.email]],
      phone: [''],
      city: [''],
      country: [''],
      linkedin: [''],
      github: [''],
      experience: this.fb.nonNullable.array<FormGroup>([]),
      projects: this.fb.nonNullable.array<FormGroup>([]),
      languages: this.fb.nonNullable.group<Record<string, string>>({}),
    });
  }

  private patchExperience(experiences: any[]): void {
    const experienceArray = this.experience;
    experienceArray.clear();

    experiences.forEach((exp) => {
      experienceArray.push(
        this.fb.nonNullable.group({
          title: [exp.title ?? ''],
          company: [exp.company ?? ''],
          period: [exp.period ?? ''],
          location: [exp.location ?? ''],
          tags: this.fb.nonNullable.array(
            (exp.tags ?? []).map((t: string) => this.fb.nonNullable.control(t)),
          ),
          bullets: this.fb.nonNullable.array(
            (exp.bullets ?? []).map((b: string) => this.fb.nonNullable.control(b)),
          ),
        }),
      );
    });
  }

  private patchProjects(projects: any[]): void {
    const projectsArray = this.projects;
    projectsArray.clear();

    projects.forEach((project) => {
      projectsArray.push(
        this.fb.nonNullable.group({
          name: [project.name ?? ''],
          description: [project.description ?? ''],
          period: [project.period ?? ''],
          technologies: this.fb.nonNullable.array(
            (project.technologies ?? []).map((t: string) => this.fb.nonNullable.control(t)),
          ),
          bullets: this.fb.nonNullable.array(
            (project.bullets ?? []).map((b: string) => this.fb.nonNullable.control(b)),
          ),
        }),
      );
    });
  }

  get contact(): FormGroup {
    return this.profileForm.get('contact') as FormGroup;
  }

  get location(): FormGroup {
    return this.profileForm.get('location') as FormGroup;
  }

  get languages(): FormArray {
    return this.profileForm.get('languages') as FormArray;
  }

  get experience(): FormArray {
    return this.profileForm.get('experience') as FormArray;
  }
  getBullets(exp: AbstractControl): FormArray {
    return exp.get('bullets') as FormArray;
  }

  addLanguage(): void {
    this.languages.push(this.fb.nonNullable.control(''));
  }

  removeLanguage(index: number): void {
    this.languages.removeAt(index);
  }

  get projects(): FormArray {
    return this.profileForm.get('projects') as FormArray;
  }

  getProjectBullets(projectIndex: number): FormArray {
    return this.projects.at(projectIndex).get('bullets') as FormArray;
  }

  addProject() {
    this.projects.push(
      this.fb.nonNullable.group({
        name: [''],
        description: [''],
        period: [''],
        technologies: this.fb.nonNullable.array<string>([]),
        bullets: this.fb.nonNullable.array<string>([]),
      }),
    );
  }

  removeProject(index: number) {
    this.projects.removeAt(index);
  }

  addProjectBullet(projectIndex: number, bullet: string = '') {
    const bullets = this.getProjectBullets(projectIndex);
    bullets.push(this.fb.nonNullable.control(bullet));
  }

  removeProjectBullet(projectIndex: number, bulletIndex: number) {
    const bullets = this.getProjectBullets(projectIndex);
    bullets.removeAt(bulletIndex);
  }

  addProjectTechnology(projectIndex: number, tech: string = '') {
    const techs = this.projects.at(projectIndex).get('technologies') as FormArray;
    techs.push(this.fb.nonNullable.control(tech));
  }

  removeProjectTechnology(projectIndex: number, techIndex: number) {
    const techs = this.projects.at(projectIndex).get('technologies') as FormArray;
    techs.removeAt(techIndex);
  }

  addExperience() {
    this.experience.push(
      this.fb.nonNullable.group({
        title: [''],
        company: [''],
        period: [''],
        location: [''],
        tags: this.fb.nonNullable.array<string>([]),
        bullets: this.fb.nonNullable.array<string>([]),
      }),
    );
  }

  removeExperience(index: number) {
    this.experience.removeAt(index);
  }

  // Add a bullet to a specific experience
  addBullet(expIndex: number, bullet: string = '') {
    const bullets = this.experience.at(expIndex).get('bullets') as FormArray;
    bullets.push(this.fb.nonNullable.control(bullet));
  }

  // Remove a bullet
  removeBullet(expIndex: number, bulletIndex: number) {
    const bullets = this.experience.at(expIndex).get('bullets') as FormArray;
    bullets.removeAt(bulletIndex);
  }

  handleUpload(event: any) {
    console.log('Files uploaded:', event.files);
  }

  submitProfileFrom() {
    console.log('Submit button clicked');
    // if (this.profileForm.invalid) {
    //   this.profileForm.markAllAsTouched();
    //   return;
    // }

    const raw = this.profileForm.getRawValue();

    this.profileData = {
      firstName: raw.firstName,
      lastName: raw.lastName,
      summary: raw.summary,

      email: raw.email,
      phone: raw.phone,
      city: raw.city,
      country: raw.country,

      linkedin: raw.linkedin,
      github: raw.github,

      languages: raw.languages,

      experience: raw.experience.map((exp: any) => ({
        title: exp.title,
        company: exp.company,
        period: exp.period,
        location: exp.location,
        tags: exp.tags ?? [],
        bullets: exp.bullets ?? [],
      })),
      projects: raw.projects.map((proj: any) => ({
        name: proj.name,
        description: proj.description,
        period: proj.period,
        technologies: proj.technologies ?? [],
        bullets: proj.bullets ?? [],
      })),
    };

    console.log('ProfileData built:', this.profileData);
    this.profileService.updateProfile(this.profileData).subscribe({
      next: () => {
        this.messageService.add({
          severity: 'success',
          summary: 'Success',
          detail: 'Porfile updated successfully.',
        });
      },
      error: () => {
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: 'Couldnt update profile',
        });
      },
    });
  }
}
