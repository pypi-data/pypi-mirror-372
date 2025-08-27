export type Links = Array<{ label: string; href: string }>;

export type AppConfig = {
  appName: string;
  header: {
    isVisible: boolean;
    insulaAppsMenuLinks?: Links;
    otherInfoMenuLinks?: Links;
  };
};

export const appConfig: AppConfig = {
  appName: 'Insula Coding (Experiment)',
  header: {
    isVisible: true,
    insulaAppsMenuLinks: [
      {
        label: 'Account Management (Awareness)',
        href: '<Awareness_link>'
      },
      {
        label: 'Processing (Intellect)',
        href: '<Intellect_link>'
      },
      {
        label: 'Visualisation & Analytics (Perception)',
        href: '<Perception_link>'
      },
      {
        label: 'Documentation',
        href: '<Documentation_link>'
      }
    ]
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
