import { IBasePalletteSetter } from '../pallette-setter';

export class LightPalletteSetter implements IBasePalletteSetter {
  readonly name: string = 'ASCEND Theme Light';
  readonly type: 'dark' | 'light' = 'light';
  setColorPallette() {
    /**
     * Borders
     */
    document.documentElement.style.setProperty(
      '--jp-border-color0',
      'var(--md-grey-400)'
    );
    document.documentElement.style.setProperty(
      '--jp-border-color1',
      'var(--md-grey-400)'
    );
    document.documentElement.style.setProperty(
      '--jp-border-color2',
      'var(--md-grey-300)'
    );
    document.documentElement.style.setProperty(
      '--jp-border-color3',
      'var(--md-grey-200)'
    );

    /**
     * Defaults use Material Design specification
     */
    document.documentElement.style.setProperty(
      '--jp-ui-font-color0',
      'rgba(0, 0, 0, 1)'
    );
    document.documentElement.style.setProperty(
      '--jp-ui-font-color1',
      'rgba(0, 0, 0, 0.87)'
    );
    document.documentElement.style.setProperty(
      '--jp-ui-font-color2',
      'rgba(0, 0, 0, 0.54)'
    );
    document.documentElement.style.setProperty(
      '--jp-ui-font-color3',
      'rgba(0, 0, 0, 0.38)'
    );

    /**
     * Defaults use Material Design specification
     */
    document.documentElement.style.setProperty(
      '--jp-content-font-color0',
      'rgba(0, 0, 0, 1)'
    );
    document.documentElement.style.setProperty(
      '--jp-content-font-color1',
      'rgba(0, 0, 0, 0.87)'
    );
    document.documentElement.style.setProperty(
      '--jp-content-font-color2',
      'rgba(0, 0, 0, 0.54)'
    );
    document.documentElement.style.setProperty(
      '--jp-content-font-color3',
      'rgba(0, 0, 0, 0.38)'
    );

    /**
     * Layout
     */
    document.documentElement.style.setProperty(
      '--jp-layout-color0',
      'var(--ascend-white)'
    );
    document.documentElement.style.setProperty(
      '--jp-layout-color1',
      'var(--ascend-white)'
    );
    document.documentElement.style.setProperty(
      '--jp-layout-color2',
      'var(--ascend-gray)'
    );
    document.documentElement.style.setProperty(
      '--jp-layout-color3',
      'var(--ascend-gray)'
    );
    document.documentElement.style.setProperty(
      '--jp-layout-color4',
      'var(--ascend-neutral-rose)'
    );

    /**
     * Inverse Layout
     */
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color0',
      '#111'
    );
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color1',
      'var(--md-grey-900)'
    );
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color2',
      'var(--md-grey-800)'
    );
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color3',
      'var(--md-grey-700)'
    );
    document.documentElement.style.setProperty(
      '--jp-inverse-layout-color4',
      'var(--md-grey-600)'
    );

    /**
     * State colors (warn, error, success, info)
     */
    document.documentElement.style.setProperty(
      '--jp-warn-color0',
      'var(--ascend-dark-magenta)'
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
      'var(--md-grey-100)'
    );
    document.documentElement.style.setProperty(
      '--jp-cell-prompt-not-active-font-color',
      'var(--md-grey-700)'
    );

    /**
     * Rendermime styles
     */
    document.documentElement.style.setProperty(
      '--jp-rendermime-error-background',
      '#fdd'
    );

    document.documentElement.style.setProperty(
      '--jp-rendermime-table-row-background',
      'var(--md-grey-100)'
    );

    document.documentElement.style.setProperty(
      '--jp-rendermime-table-row-hover-background',
      'var(--md-grey-200)'
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
      '#999'
    );
  }
}
