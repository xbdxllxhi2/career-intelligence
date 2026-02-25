import { Injectable, inject } from '@angular/core';
import { KeycloakService } from 'keycloak-angular';
import { KeycloakProfile } from 'keycloak-js';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private keycloak = inject(KeycloakService);

  get isLoggedIn(): boolean {
    return this.keycloak.isLoggedIn();
  }

  get userProfile(): Promise<KeycloakProfile> {
    return this.keycloak.loadUserProfile();
  }

  get username(): string {
    return this.keycloak.getUsername();
  }

  get token(): Promise<string> {
    return this.keycloak.getToken();
  }

  get userRoles(): string[] {
    return this.keycloak.getUserRoles();
  }

  login(): Promise<void> {
    return this.keycloak.login();
  }

  logout(): Promise<void> {
    return this.keycloak.logout(window.location.origin);
  }

  hasRole(role: string): boolean {
    return this.keycloak.isUserInRole(role);
  }
}
