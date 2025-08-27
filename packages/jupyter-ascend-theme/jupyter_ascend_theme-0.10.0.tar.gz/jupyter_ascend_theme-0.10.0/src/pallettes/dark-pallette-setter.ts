import { IBasePalletteSetter } from '../pallette-setter';

export class DarkPalletteSetter implements IBasePalletteSetter {
  readonly name: string = 'ASCEND Theme Dark';
  readonly type: 'dark' | 'light' = 'dark';
  setColorPallette() {
    /**
     * Borders
     */
    document.documentElement.style.setProperty(
      '--jp-border-color0',
      'var(--md-grey-200)'
    );
    document.documentElement.style.setProperty(
      '--jp-border-color1',
      'var(--md-grey-300)'
    );
    document.documentElement.style.setProperty(
      '--jp-border-color2',
      'var(--md-grey-400)'
    );
    document.documentElement.style.setProperty(
      '--jp-border-color3',
      'var(--md-grey-400)'
    );

    /**
     * Defaults use Material Design specification
     */
    document.documentElement.style.setProperty(
      '--jp-ui-font-color0',
      'rgba(255, 255, 255, 1)'
    );
    document.documentElement.style.setProperty(
      '--jp-ui-font-color1',
      'rgba(255, 255, 255, 1)'
    );
    document.documentElement.style.setProperty(
      '--jp-ui-font-color2',
      'rgba(255, 255, 255, 0.9)'
    );
    document.documentElement.style.setProperty(
      '--jp-ui-font-color3',
      'rgba(255, 255, 255, 0.8)'
    );

    /**
     * Defaults use Material Design specification
     */
    document.documentElement.style.setProperty(
      '--jp-content-font-color0',
      'rgba(255, 255, 255, 1)'
    );
    document.documentElement.style.setProperty(
      '--jp-content-font-color1',
      'rgba(255, 255, 255, 0.9)'
    );
    document.documentElement.style.setProperty(
      '--jp-content-font-color2',
      'rgba(255, 255, 255, 0.8)'
    );
    document.documentElement.style.setProperty(
      '--jp-content-font-color3',
      'rgba(255, 255, 255, 0.8)'
    );

    /**
     * Layout
     */
    document.documentElement.style.setProperty(
      '--jp-layout-color0',
      'var(--ascend-darker-blue)'
    );
    document.documentElement.style.setProperty(
      '--jp-layout-color1',
      'var(--ascend-darker-blue)'
    );
    document.documentElement.style.setProperty(
      '--jp-layout-color2',
      'var(--ascend-dark-blue)'
    );
    document.documentElement.style.setProperty(
      '--jp-layout-color3',
      'var(--ascend-dark-blue)'
    );
    document.documentElement.style.setProperty(
      '--jp-layout-color4',
      'var(--ascend-dark-magenta)'
    );

    /**
     * Inverse Layout
     */
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color0',
      'rgb(255, 255, 255)'
    );
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color1',
      'rgb(255, 255, 255)'
    );
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color2',
      'rgba(255, 255, 255, 0.87)'
    );
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color3',
      'rgba(255, 255, 255, 0.87)'
    );
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color4',
      'rgba(255, 255, 255, 0.87)'
    );

    /**
     * State colors (warn, error, success, info)
     */
    document.documentElement.style.setProperty(
      '--jp-warn-color0',
      'var--ascend-dark-magenta)'
    );
    document.documentElement.style.setProperty(
      '--jp-warn-color1',
      'var(--ascend-magenta)'
    );
    document.documentElement.style.setProperty(
      '--jp-warn-color2',
      'var(--ascend-magenta)'
    );
    document.documentElement.style.setProperty(
      '--jp-warn-color3',
      'var(--ascend-neutral-magenta)'
    );

    /**
     * Cell specific styles
     */
    document.documentElement.style.setProperty(
      '--jp-cell-editor-background',
      '#353535'
    );
    document.documentElement.style.setProperty(
      '--jp-cell-prompt-not-active-font-color',
      'var(--md-grey-200)'
    );

    /**
     * Rendermime styles
     */
    document.documentElement.style.setProperty(
      '--jp-rendermime-error-background',
      'var(--ascend-dark-blue)'
    );

    document.documentElement.style.setProperty(
      '--jp-rendermime-table-row-background',
      'var(--md-grey-800)'
    );

    document.documentElement.style.setProperty(
      '--jp-rendermime-table-row-hover-background',
      'var(--md-grey-700)'
    );

    /**
     * Code mirror specific styles
     */
    document.documentElement.style.setProperty(
      '--jp-mirror-editor-operator-color',
      '#a2f'
    );
    document.documentElement.style.setProperty(
      '--jp-mirror-editor-meta-color',
      '#a2f'
    );
    document.documentElement.style.setProperty(
      '--jp-mirror-editor-attribute-color',
      'rgb(255, 255, 255)'
    );
  }
}
