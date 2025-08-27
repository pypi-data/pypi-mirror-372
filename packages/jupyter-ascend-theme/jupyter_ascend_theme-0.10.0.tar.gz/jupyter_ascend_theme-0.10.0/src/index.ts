import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { IThemeManager } from '@jupyterlab/apputils';

import { appConfig } from './configuration';
import { IBasePalletteSetter } from './pallette-setter';
import { DarkPalletteSetter, LightPalletteSetter } from './pallettes';
import { initAppHeader, initiAppFaviconAndTitle } from './utils';

initiAppFaviconAndTitle();

/**
 * Initialization data for the jupyter_ascend_theme extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter_ascend_theme:plugin',
  description: 'The JupyterLab ASCEND theme',
  autoStart: true,
  requires: [IThemeManager],
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
    app.started.then(() => {
      if (appConfig.header.isVisible) {
        initAppHeader();
      }
    });

    /**
     * Due to the current limitation of not being able to register multiple themes
     * [https://github.com/jupyterlab/jupyterlab/issues/14202]
     * in the same extension when each theme has its own separate CSS file, we
     * handle theme variants by storing the color palette in TypeScript files and
     * loading them dynamically through a script. This approach allows us to load
     * a base theme ('jupyter-cgi-theme/index.css') and then override the necessary color properties
     * based on the selected palette.
     *
     * * Note: In development mode, the path to 'index.css' might differ because the plugin
     * expects the CSS file to be located in the mounted app's root folder (lib).
     */
    const pallettesSetters: (new () => IBasePalletteSetter)[] = [
      LightPalletteSetter,
      DarkPalletteSetter
    ];
    const baseTheme = 'jupyter_ascend_theme/index.css';

    pallettesSetters.forEach(Pallette => {
      const pallette = new Pallette();

      manager.register({
        name: pallette.name,
        isLight: pallette.type === 'light',
        load: () => {
          pallette.setColorPallette();
          return manager.loadCSS(baseTheme);
        },
        unload: () => Promise.resolve(undefined)
      });
    });
  }
};

export default plugin;
