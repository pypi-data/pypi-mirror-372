import { ICollaborativeDrive } from '@jupyter/collaborative-drive';
import { JupyterGISDocumentWidget } from '@jupytergis/base';
import { JupyterGISModel, IJupyterGISTracker, IJGISExternalCommandRegistry, IJGISFormSchemaRegistry, IAnnotationModel } from '@jupytergis/schema';
import { IEditorMimeTypeService } from '@jupyterlab/codeeditor';
import { ConsolePanel, IConsoleTracker } from '@jupyterlab/console';
import { ABCWidgetFactory, DocumentRegistry } from '@jupyterlab/docregistry';
import { IRenderMimeRegistry } from '@jupyterlab/rendermime';
import { ServiceManager } from '@jupyterlab/services';
import { IStateDB } from '@jupyterlab/statedb';
import { CommandRegistry } from '@lumino/commands';
interface IOptions extends DocumentRegistry.IWidgetFactoryOptions {
    tracker: IJupyterGISTracker;
    commands: CommandRegistry;
    externalCommandRegistry: IJGISExternalCommandRegistry;
    manager?: ServiceManager.IManager;
    contentFactory?: ConsolePanel.IContentFactory;
    mimeTypeService?: IEditorMimeTypeService;
    rendermime?: IRenderMimeRegistry;
    consoleTracker?: IConsoleTracker;
    backendCheck?: () => boolean;
    drive?: ICollaborativeDrive | null;
    formSchemaRegistry: IJGISFormSchemaRegistry;
    state: IStateDB;
    annotationModel: IAnnotationModel;
}
export declare class JupyterGISDocumentWidgetFactory extends ABCWidgetFactory<JupyterGISDocumentWidget, JupyterGISModel> {
    private options;
    constructor(options: IOptions);
    /**
     * Create a new widget given a context.
     *
     * @param context Contains the information of the file
     * @returns The widget
     */
    protected createNewWidget(context: DocumentRegistry.IContext<JupyterGISModel>): JupyterGISDocumentWidget;
    private _commands;
    private _externalCommandRegistry;
    private _backendCheck?;
    private _contentsManager?;
}
export {};
