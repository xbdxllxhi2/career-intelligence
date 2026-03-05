import { KeycloakService } from 'keycloak-angular';
import { environment } from '../../../environments/environments';

export function initializeKeycloak(keycloak: KeycloakService): () => Promise<boolean> {
  return () =>
    keycloak.init({
      config: {
        url: environment.keycloak.url,
        realm: environment.keycloak.realm,
        clientId: environment.keycloak.clientId
      },
      initOptions: {
        onLoad: 'check-sso',
        silentCheckSsoRedirectUri: window.location.origin + '/silent-check-sso.html',
        checkLoginIframe: false
      },
      enableBearerInterceptor: true,
      bearerPrefix: 'Bearer',
      bearerExcludedUrls: ['/assets', '/public', '/i18n'],
      shouldAddToken: (request) => {
        const { url } = request;
        // Always add token for API requests
        const isApiUrl = url.startsWith(environment.apiUrl);
        // Add token for same-origin requests (excluding assets)
        const isSameOrigin = url.startsWith(window.location.origin) && 
                            !url.includes('/assets/') && 
                            !url.includes('/i18n/');
        return isApiUrl || isSameOrigin;
      }
    }).catch((error) => {
      console.error('Keycloak initialization failed:', error);
      return false;
    });
}
