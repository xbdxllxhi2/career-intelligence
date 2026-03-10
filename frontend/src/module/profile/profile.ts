import { Component, inject, Input, OnInit } from '@angular/core';
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
import { UserProfile, EducationEntry, ExperienceEntry, ProjectEntry, CertificationEntry } from '../../models/interface/cv-profile';
import { SkeletonModule } from 'primeng/skeleton';
import { CommonModule } from '@angular/common';
import { DatePickerModule } from 'primeng/datepicker';
import { FloatLabelModule } from 'primeng/floatlabel';
import { ProfileService } from '../../service/profile-service';
import { ToastModule } from 'primeng/toast';
import { SelectModule } from 'primeng/select';
import { MessageService } from 'primeng/api';
import { KeycloakService } from 'keycloak-angular';
import { environment } from '../../environments/environments';

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
    SelectModule,
  ],
  providers: [MessageService],
  templateUrl: './profile.html',
  styleUrl: './profile.scss',
})
export class Profile {
  @Input() conversation: QuestionAnswer[] = [];

  private keycloak = inject(KeycloakService);
  isAuthenticated = false;
  isParsingResume = false;
  isLoadingProfile = true;

  profileData!: UserProfile;

  profileForm!: FormGroup;

  studyYearOptions = [
    { label: '1st Year', value: 1 },
    { label: '2nd Year', value: 2 },
    { label: '3rd Year', value: 3 },
    { label: '4th Year', value: 4 },
    { label: '5th Year', value: 5 },
    { label: 'Graduate', value: 6 },
  ];

  constructor(
    private fb: FormBuilder,
    private messageService: MessageService,
    private profileService: ProfileService,
  ) {}

  ngOnInit(): void {
    this.isAuthenticated = environment.keycloak.enabled ? this.keycloak.isLoggedIn() : true;
    this.initForm();
    if (this.isAuthenticated) {
      this.initProfileData();
    }
  }

  login(): void {
    this.keycloak.login({
      redirectUri: window.location.origin + '/profile'
    });
  }

  private initProfileData(): void {
    this.isLoadingProfile = true;
    this.profileService.getUserProfile().subscribe({
      next: (profile) => {
        console.log('Got Profile ', profile);
        this.profileData = profile;
        this.profileForm.patchValue(this.profileData);
        if (profile.experience?.length) {
          this.patchExperience(profile.experience);
        }

        if (profile.education?.length) {
          this.patchEducation(profile.education);
        }

        if (profile.projects?.length) {
          this.patchProjects(profile.projects);
        }

        if (profile.certifications?.length) {
          this.patchCertifications(profile.certifications);
        }

        if (profile.languages && Object.keys(profile.languages).length) {
          this.patchSpokenLanguages(profile.languages);
        }
        this.isLoadingProfile = false;
      },
      error: () => {
        this.isLoadingProfile = false;
      }
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
      portfolio: [''],
      experience: this.fb.nonNullable.array<FormGroup>([]),
      education: this.fb.nonNullable.array<FormGroup>([]),
      projects: this.fb.nonNullable.array<FormGroup>([]),
      certifications: this.fb.nonNullable.array<FormGroup>([]),
      spokenLanguages: this.fb.nonNullable.array<FormGroup>([]),
      languages: this.fb.nonNullable.group<Record<string, string>>({}),
    });
  }

  private patchExperience(experiences: ExperienceEntry[]): void {
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

  private patchEducation(educations: EducationEntry[]): void {
    const educationArray = this.education;
    educationArray.clear();

    educations.forEach((edu) => {
      // Map API fields to form fields: year -> period, school/institution -> institution, coursework -> field
      educationArray.push(
        this.fb.nonNullable.group({
          degree: [edu.degree ?? ''],
          institution: [edu.institution ?? edu.school ?? ''],
          period: [edu.year ?? ''],
          field: [edu.coursework ?? ''],
          grade: [''],
          studyYear: [null],
        }),
      );
    });
  }

  private patchProjects(projects: ProjectEntry[]): void {
    const projectsArray = this.projects;
    projectsArray.clear();

    projects.forEach((project) => {
      // Map API fields to form fields: year -> period, tags -> technologies
      projectsArray.push(
        this.fb.nonNullable.group({
          name: [project.name ?? ''],
          description: [project.description ?? ''],
          period: [project.year ?? ''],
          technologies: this.fb.nonNullable.array(
            (project.tags ?? []).map((t: string) => this.fb.nonNullable.control(t)),
          ),
          bullets: this.fb.nonNullable.array(
            (project.bullets ?? []).map((b: string) => this.fb.nonNullable.control(b)),
          ),
        }),
      );
    });
  }

  private patchCertifications(certifications: CertificationEntry[]): void {
    const certificationsArray = this.certifications;
    certificationsArray.clear();

    certifications.forEach((cert) => {
      certificationsArray.push(
        this.fb.nonNullable.group({
          name: [cert.name ?? ''],
          issuer: [cert.issuer ?? ''],
          date: [cert.date ?? ''],
          credentialId: [cert.credentialId ?? ''],
          url: [cert.url ?? ''],
        }),
      );
    });
  }

  private patchSpokenLanguages(languages: Record<string, string>): void {
    const languagesArray = this.spokenLanguages;
    languagesArray.clear();

    Object.entries(languages).forEach(([name, level]) => {
      languagesArray.push(
        this.fb.nonNullable.group({
          name: [name],
          level: [level],
        }),
      );
    });
  }

  private convertLanguagesToRecord(languages?: Array<{name: string; proficiency: string}>): Record<string, string> {
    if (!languages || languages.length === 0) {
      return {};
    }
    return languages.reduce((acc, lang) => {
      if (lang.name) {
        acc[lang.name] = lang.proficiency || '';
      }
      return acc;
    }, {} as Record<string, string>);
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

  get education(): FormArray {
    return this.profileForm.get('education') as FormArray;
  }

  addEducation() {
    this.education.push(
      this.fb.nonNullable.group({
        degree: [''],
        institution: [''],
        period: [''],
        field: [''],
        grade: [''],
        studyYear: [null as number | null],
      }),
    );
  }

  removeEducation(index: number) {
    this.education.removeAt(index);
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

  // Certifications
  get certifications(): FormArray {
    return this.profileForm.get('certifications') as FormArray;
  }

  addCertification() {
    this.certifications.push(
      this.fb.nonNullable.group({
        name: [''],
        issuer: [''],
        date: [''],
        credentialId: [''],
        url: [''],
      }),
    );
  }

  removeCertification(index: number) {
    this.certifications.removeAt(index);
  }

  // Spoken Languages
  get spokenLanguages(): FormArray {
    return this.profileForm.get('spokenLanguages') as FormArray;
  }

  languageLevelOptions = [
    { label: 'Native', value: 'native' },
    { label: 'Fluent', value: 'fluent' },
    { label: 'Advanced', value: 'advanced' },
    { label: 'Intermediate', value: 'intermediate' },
    { label: 'Basic', value: 'basic' },
  ];

  addSpokenLanguage() {
    this.spokenLanguages.push(
      this.fb.nonNullable.group({
        name: [''],
        level: [''],
      }),
    );
  }

  removeSpokenLanguage(index: number) {
    this.spokenLanguages.removeAt(index);
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
    const file = event.files?.[0];
    if (!file) {
      return;
    }

    this.isParsingResume = true;
    this.profileService.parseResume(file).subscribe({
      next: (parsedProfile) => {
        // Patch basic fields
        this.profileForm.patchValue({
          firstName: parsedProfile.firstName || '',
          lastName: parsedProfile.lastName || '',
          email: parsedProfile.email || '',
          phone: parsedProfile.phone || '',
          city: parsedProfile.city || '',
          country: parsedProfile.country || '',
          linkedin: parsedProfile.linkedin || '',
          github: parsedProfile.github || '',
          summary: parsedProfile.summary || '',
        });

        // Patch languages
        if (parsedProfile.languages?.length) {
          const languagesRecord = this.convertLanguagesToRecord(parsedProfile.languages as any);
          this.patchSpokenLanguages(languagesRecord);
        }

        // Patch certifications
        if (parsedProfile.certifications?.length) {
          this.patchCertifications(parsedProfile.certifications);
        }

        // Patch experience
        if (parsedProfile.experience?.length) {
          this.patchExperience(parsedProfile.experience as ExperienceEntry[]);
        }

        // Patch education - pass API format directly, patchEducation handles the mapping
        if (parsedProfile.education?.length) {
          this.patchEducation(parsedProfile.education.map(edu => ({
            degree: edu.degree,
            school: edu.school,
            institution: edu.institution,
            year: edu.year,
            coursework: edu.coursework,
          })));
        }

        // Patch projects - pass API format directly, patchProjects handles the mapping
        if (parsedProfile.projects?.length) {
          this.patchProjects(parsedProfile.projects.map(proj => ({
            name: proj.name,
            description: proj.description,
            year: proj.year,
            tags: proj.tags || [],
            bullets: proj.bullets || [],
          })));
        }

        this.messageService.add({
          severity: 'success',
          summary: 'Resume Parsed',
          detail: 'Your profile has been populated from your resume. Please review and save.',
        });
        this.isParsingResume = false;
      },
      error: (err) => {
        console.error('Error parsing resume:', err);
        this.messageService.add({
          severity: 'error',
          summary: 'Error',
          detail: err.error?.detail || 'Failed to parse resume. Please try again or fill manually.',
        });
        this.isParsingResume = false;
      },
    });
  }

  submitProfileFrom() {
    console.log('Submit button clicked');
    // if (this.profileForm.invalid) {
    //   this.profileForm.markAllAsTouched();
    //   return;
    // }

    const raw = this.profileForm.getRawValue();

    // Convert spokenLanguages array to languages record
    const languagesRecord: Record<string, string> = {};
    (raw.spokenLanguages || []).forEach((lang: { name: string; level: string }) => {
      if (lang.name) {
        languagesRecord[lang.name] = lang.level || '';
      }
    });

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

      languages: languagesRecord,

      education: raw.education.map((edu: any) => ({
        degree: edu.degree,
        institution: edu.institution,
        year: edu.period || '',
        school: edu.institution,
        coursework: edu.field,
      })),

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
        year: proj.period,
        tags: proj.technologies ?? [],
        bullets: proj.bullets ?? [],
      })),

      certifications: raw.certifications.map((cert: any) => ({
        name: cert.name,
        issuer: cert.issuer,
        date: cert.date,
        credentialId: cert.credentialId,
        url: cert.url,
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
