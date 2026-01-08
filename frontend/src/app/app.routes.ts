import { Routes } from '@angular/router';

export const routes: Routes = [
    {path:'', loadComponent: () => import('../module/home/home').then(m => m.Home)},
    {path:'profile', loadComponent: () => import('../module/profile/profile').then(m => m.Profile)},
    {path:'jobs', loadComponent: () => import('../module/job-finder/job-finder').then(m => m.JobFinder)},
    {path:'applications', loadComponent: () => import('../module/applications/applications').then(m => m.Applications)},
    {path:'inbox', loadComponent: () => import('../module/inbox/inbox').then(m => m.Inbox),},
    {path:'resume', loadComponent:()=> import('../module/resume/resume').then(m=> m.Resume)}
];
