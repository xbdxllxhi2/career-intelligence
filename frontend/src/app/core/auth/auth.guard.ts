import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { KeycloakService } from 'keycloak-angular';

export const authGuard: CanActivateFn = async () => {
  const keycloak = inject(KeycloakService);
  const router = inject(Router);

  const isAuthenticated = keycloak.isLoggedIn();
console.log('AuthGuard: User is authenticated:', isAuthenticated);
  if (!isAuthenticated) {
    await keycloak.login({
      redirectUri: window.location.origin + router.url
    });
    return false;
  }

  return true;
};
