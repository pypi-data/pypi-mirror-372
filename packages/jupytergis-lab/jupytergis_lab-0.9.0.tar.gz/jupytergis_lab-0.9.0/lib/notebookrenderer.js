import { ICollaborativeDrive } from '@jupyter/collaborative-drive';
import { JupyterGISOutputWidget, JupyterGISPanel, ToolbarWidget, } from '@jupytergis/base';
import { IJGISExternalCommandRegistryToken, IJupyterGISDocTracker, JupyterGISModel, IJGISFormSchemaRegistryToken, IAnnotationToken, } from '@jupytergis/schema';
import { showErrorMessage } from '@jupyterlab/apputils';
import { ConsolePanel } from '@jupyterlab/console';
import { PathExt } from '@jupyterlab/coreutils';
import { NotebookPanel } from '@jupyterlab/notebook';
import { ISettingRegistry } from '@jupyterlab/settingregistry';
import { IStateDB } from '@jupyterlab/statedb';
import { MessageLoop } from '@lumino/messaging';
import { Panel, Widget } from '@lumino/widgets';
import { IJupyterYWidgetManager, JupyterYDoc, JupyterYModel, } from 'yjs-widgets';
export const CLASS_NAME = 'jupytergis-notebook-widget';
export class YJupyterGISModel extends JupyterYModel {
}
export class YJupyterGISLuminoWidget extends Panel {
    constructor(options) {
        super();
        /**
         * Build the widget and add it to the panel.
         * @param options
         */
        this._buildWidget = (options) => {
            const { commands, model, externalCommands, tracker, formSchemaRegistry, state, annotationModel, } = options;
            const content = new JupyterGISPanel({
                model,
                commandRegistry: commands,
                formSchemaRegistry,
                state,
                annotationModel,
            });
            let toolbar = undefined;
            if (model.filePath) {
                toolbar = new ToolbarWidget({
                    commands,
                    model,
                    externalCommands: (externalCommands === null || externalCommands === void 0 ? void 0 : externalCommands.getCommands()) || [],
                });
            }
            this._jgisWidget = new JupyterGISOutputWidget({
                model,
                content,
                toolbar,
            });
            this.addWidget(this._jgisWidget);
            tracker === null || tracker === void 0 ? void 0 : tracker.add(this._jgisWidget);
        };
        const { model } = options;
        this.addClass(CLASS_NAME);
        this._buildWidget(options);
        // If the filepath was not set when building the widget, the toolbar is not built.
        // The widget has to be built again to include the toolbar.
        const onchange = (_, args) => {
            if (args.stateChange) {
                args.stateChange.forEach((change) => {
                    var _a;
                    if (change.name === 'path') {
                        (_a = this.layout) === null || _a === void 0 ? void 0 : _a.removeWidget(this._jgisWidget);
                        this._jgisWidget.dispose();
                        this._buildWidget(options);
                    }
                });
            }
        };
        model.sharedModel.changed.connect(onchange);
    }
    get jgisWidget() {
        return this._jgisWidget;
    }
}
export const notebookRendererPlugin = {
    id: 'jupytergis:yjswidget-plugin',
    autoStart: true,
    optional: [
        IJGISExternalCommandRegistryToken,
        IJupyterGISDocTracker,
        IJupyterYWidgetManager,
        ICollaborativeDrive,
        IStateDB,
        IJGISFormSchemaRegistryToken,
        IAnnotationToken,
        ISettingRegistry,
    ],
    activate: (app, externalCommandRegistry, jgisTracker, yWidgetManager, drive, formSchemaRegistry, state, annotationModel, settingRegistry) => {
        if (!yWidgetManager) {
            console.error('Missing IJupyterYWidgetManager token!');
            return;
        }
        class YJupyterGISModelFactory extends YJupyterGISModel {
            async initialize(commMetadata) {
                const { path, format, contentType } = commMetadata;
                const fileFormat = format;
                if (!drive) {
                    showErrorMessage('Error using the JupyterGIS Python API', 'You cannot use the JupyterGIS Python API without a collaborative drive. You need to install a package providing collaboration features (e.g. jupyter-collaboration).');
                    throw new Error('Failed to create the YDoc without a collaborative drive');
                }
                // The path of the project is relative to the path of the notebook
                let currentWidgetPath = '';
                const currentWidget = app.shell.currentWidget;
                if (currentWidget instanceof NotebookPanel ||
                    currentWidget instanceof ConsolePanel) {
                    currentWidgetPath = currentWidget.sessionContext.path;
                }
                let localPath = '';
                if (path) {
                    localPath = PathExt.join(PathExt.dirname(currentWidgetPath), path);
                    // If the file does not exist yet, create it
                    try {
                        await app.serviceManager.contents.get(localPath);
                    }
                    catch (e) {
                        await app.serviceManager.contents.save(localPath, {
                            content: btoa('{}'),
                            format: 'base64',
                        });
                    }
                }
                else {
                    // If the user did not provide a path, do not create
                    localPath = PathExt.join(PathExt.dirname(currentWidgetPath), 'unsaved_project');
                }
                const sharedModel = drive.sharedModelFactory.createNew({
                    path: localPath,
                    format: fileFormat,
                    contentType,
                    collaborative: true,
                });
                this.jupyterGISModel = new JupyterGISModel({
                    sharedModel: sharedModel,
                    settingRegistry,
                });
                this.jupyterGISModel.contentsManager = app.serviceManager.contents;
                this.jupyterGISModel.filePath = localPath;
                this.ydoc = this.jupyterGISModel.sharedModel.ydoc;
                this.sharedModel = new JupyterYDoc(commMetadata, this.ydoc);
            }
        }
        class YJupyterGISWidget {
            constructor(yModel, node) {
                this.yModel = yModel;
                this.node = node;
                const widget = new YJupyterGISLuminoWidget({
                    commands: app.commands,
                    model: yModel.jupyterGISModel,
                    externalCommands: externalCommandRegistry,
                    tracker: jgisTracker,
                    annotationModel,
                    state,
                    formSchemaRegistry,
                });
                this._jgisWidget = widget.jgisWidget;
                MessageLoop.sendMessage(widget, Widget.Msg.BeforeAttach);
                node.appendChild(widget.node);
                MessageLoop.sendMessage(widget, Widget.Msg.AfterAttach);
            }
            dispose() {
                // Dispose of the widget.
                this._jgisWidget.dispose();
            }
        }
        yWidgetManager.registerWidget('@jupytergis:widget', YJupyterGISModelFactory, YJupyterGISWidget);
    },
};
