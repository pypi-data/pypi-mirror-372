import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IThemeManager } from '@jupyterlab/apputils';

/**
 * Initialization data for the jupyter_ascend_theme extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter_ascend_theme:plugin',
  description: 'The JupyterLab ASCEND theme',
  autoStart: true,
  requires: [IThemeManager],
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
    console.log('JupyterLab extension jupyter_ascend_theme is activated!');
    const style = 'jupyter_ascend_theme/index.css';

    manager.register({
      name: 'jupyter_ascend_theme',
      isLight: true,
      load: () => manager.loadCSS(style),
      unload: () => Promise.resolve(undefined)
    });
  }
};

export default plugin;
