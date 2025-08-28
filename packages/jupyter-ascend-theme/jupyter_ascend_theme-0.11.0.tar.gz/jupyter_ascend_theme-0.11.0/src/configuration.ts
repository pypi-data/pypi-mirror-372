export type Links = Array<{ label: string; href: string }>;

export type AppConfig = {
  appName: string;
  header: {
    isVisible: boolean;
    getInsulaAppsMenuLinks: () => Links | undefined;
    otherInfoMenuLinks?: Links;
  };
};

export const appConfig: AppConfig = {
  appName: 'Insula Coding (Experiment)',
  header: {
    isVisible: true,
    getInsulaAppsMenuLinks: () => {
      const linksFromEnvVariables = (
        window as Window & { __MENU_LINKS__?: Links }
      ).__MENU_LINKS__;

      if (linksFromEnvVariables && linksFromEnvVariables.length > 0) {
        return linksFromEnvVariables;
      } else {
        let environmentNameFromUrl: 'earthcare' | 'biomass' | undefined =
          undefined;
        const originUrl = window.location.origin;

        if (originUrl.toLowerCase().includes('earthcare')) {
          environmentNameFromUrl = 'earthcare';
        } else if (originUrl.toLowerCase().includes('biomass')) {
          environmentNameFromUrl = 'biomass';
        }

        if (environmentNameFromUrl) {
          return [
            {
              label: 'Visualisation & Analytics (Perception)',
              href: `https://${environmentNameFromUrl}.pal.maap.eo.esa.int/perception`
            },
            {
              label: 'Processing (Intellect)',
              href: `https://${environmentNameFromUrl}.pal.maap.eo.esa.int/intellect`
            },
            {
              label: 'Account Management (Awareness)',
              href: `https://${environmentNameFromUrl}.pal.maap.eo.esa.int/awareness`
            },
            {
              label: 'Documentation',
              href: `https://portal.maap.eo.esa.int/ini/services/PAL/${environmentNameFromUrl}/`
            }
          ];
        } else {
          return undefined;
        }
      }
    }
    // otherInfoMenuLinks: [
    //   {
    //     label: 'Docs',
    //     href: '<Docs_link>'
    //   },
    //   {
    //     label: 'Support',
    //     href: '<Support_link>'
    //   }
    // ]
  }
};
