export type Links = Array<{ label: string; href: string }>;

export type AppConfig = {
  appName: string;
  header: {
    isVisible: boolean;
    getInsulaAppsMenuLinks: () => Promise<Links | undefined>;
    otherInfoMenuLinks?: Links;
  };
};

export const appConfig: AppConfig = {
  appName: 'Insula Coding (Experiment)',
  header: {
    isVisible: true,
    getInsulaAppsMenuLinks: async () => {
      let linksFromJupyterHubEnvVariables: Links | undefined;

      try {
        const response = await fetch('/hub/home');
        const textResponse = await response.text();

        // Regex to extract the window.__MENU_LINKS__ JSON
        const match = textResponse.match(
          /window\.__MENU_LINKS__\s*=\s*(\[[\s\S]*?\]);/
        );

        if (match && match[1]) {
          linksFromJupyterHubEnvVariables = JSON.parse(match[1]);
        }
      } catch (error) {
        console.warn('Failed to fetch menu links from /hub/home', error);
      }

      if (
        linksFromJupyterHubEnvVariables &&
        linksFromJupyterHubEnvVariables.length > 0
      ) {
        console.warn('Using menu links from /hub/home');
        return linksFromJupyterHubEnvVariables;
      }

      // Fallback logic based on environment name in the URL
      let environmentNameFromUrl: 'earthcare' | 'biomass' | undefined;
      const originUrl = window.location.origin.toLowerCase();

      if (originUrl.includes('earthcare')) {
        environmentNameFromUrl = 'earthcare';
      } else if (originUrl.includes('biomass')) {
        environmentNameFromUrl = 'biomass';
      }

      if (environmentNameFromUrl) {
        console.warn('Using menu links built form URL');
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
      }

      return undefined;
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
