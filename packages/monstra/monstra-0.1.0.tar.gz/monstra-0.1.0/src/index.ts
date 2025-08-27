import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

/**
 * Initialization data for the jupyter-monstra extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-monstra:plugin',
  description: 'A JupyterLab extension.',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension jupyter-monstra is activated!');
  }
};

export default plugin;
