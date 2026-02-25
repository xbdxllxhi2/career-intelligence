import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';
import { environment } from '../../../environments/environments';

export const authGuard: CanActivateFn = async () => {
  // Skip auth check if Keycloak is disabled
  if (!environment.keycloak.enabled) {
    return true;
  }

  const keycloak = inject(KeycloakService);
  const router = inject(Router);

  const isAuthenticated = keycloak.isLoggedIn();

  if (!isAuthenticated) {
    await keycloak.login({
      redirectUri: window.location.origin + router.url
    });
    return false;
  }

  return true;
};
