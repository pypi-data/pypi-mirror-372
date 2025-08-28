import { JupyterGISOutputWidget, JupyterGISTracker } from '@jupytergis/base';
import { IJGISExternalCommandRegistry, JupyterGISModel, IJGISFormSchemaRegistry, IAnnotationModel } from '@jupytergis/schema';
import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { IStateDB } from '@jupyterlab/statedb';
import { CommandRegistry } from '@lumino/commands';
import { Panel } from '@lumino/widgets';
import { JupyterYModel } from 'yjs-widgets';
export interface ICommMetadata {
    create_ydoc: boolean;
    path: string;
    format: string;
    contentType: string;
    ymodel_name: string;
}
export declare const CLASS_NAME = "jupytergis-notebook-widget";
export declare class YJupyterGISModel extends JupyterYModel {
    jupyterGISModel: JupyterGISModel;
}
export declare class YJupyterGISLuminoWidget extends Panel {
    constructor(options: IOptions);
    get jgisWidget(): JupyterGISOutputWidget;
    /**
     * Build the widget and add it to the panel.
     * @param options
     */
    private _buildWidget;
    private _jgisWidget;
}
interface IOptions {
    commands: CommandRegistry;
    model: JupyterGISModel;
    externalCommands?: IJGISExternalCommandRegistry;
    tracker?: JupyterGISTracker;
    formSchemaRegistry?: IJGISFormSchemaRegistry;
    state?: IStateDB;
    annotationModel?: IAnnotationModel;
}
export declare const notebookRendererPlugin: JupyterFrontEndPlugin<void>;
export {};
