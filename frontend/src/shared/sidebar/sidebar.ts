import { Component, Input } from '@angular/core';
import { DrawerModule } from 'primeng/drawer';
import  { ButtonModule } from 'primeng/button';
import { MenuModule } from 'primeng/menu';
import { MenuItem } from 'primeng/api';
import { RouterLinkActive } from "@angular/router";

@Component({
  selector: 'app-sidebar',
  imports: [DrawerModule, ButtonModule, MenuModule, RouterLinkActive],
  templateUrl: './sidebar.html',
  styleUrl: './sidebar.scss',
})
export class Sidebar {
  visible = false;
  active: string = '';

  items:MenuItem[] = [
    { label: "Home", icon: "pi pi-home", routerLink: ["/" ], routerLinkActiveOptions: { exact: true }},
    { label: "Profile", icon: "pi pi-user", routerLink: ["/profile" ]},
    { label: "AI Job Finder", icon: "pi pi-code", routerLink: ["/ai-job-finder" ]},
    { label: "Applications", icon: "pi pi-briefcase", routerLink: ["/applications" ]},
    {label: "Messages", icon: "pi pi-inbox", routerLink: ["/messages" ] }
  ]

  items2:MenuItem[] = [
    { label: "Logout", icon: "pi pi-sign-out", routerLink: ["/logout" ]},
    { label: "Settings", icon: "pi pi-cog", routerLink: ["/settings" ]},
    { label: "Contact", icon: "pi pi-envelope", routerLink: ["/contact" ] }
  ]
}
