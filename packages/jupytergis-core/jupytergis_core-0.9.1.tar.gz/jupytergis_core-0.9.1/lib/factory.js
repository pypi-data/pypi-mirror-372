var __rest = (this && this.__rest) || function (s, e) {
    var t = {};
    for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p) && e.indexOf(p) < 0)
        t[p] = s[p];
    if (s != null && typeof Object.getOwnPropertySymbols === "function")
        for (var i = 0, p = Object.getOwnPropertySymbols(s); i < p.length; i++) {
            if (e.indexOf(p[i]) < 0 && Object.prototype.propertyIsEnumerable.call(s, p[i]))
                t[p[i]] = s[p[i]];
        }
    return t;
};
import { JupyterGISPanel, JupyterGISDocumentWidget, ToolbarWidget, } from '@jupytergis/base';
import { ABCWidgetFactory } from '@jupyterlab/docregistry';
export class JupyterGISDocumentWidgetFactory extends ABCWidgetFactory {
    constructor(options) {
        var _a;
        const { backendCheck, externalCommandRegistry } = options, rest = __rest(options, ["backendCheck", "externalCommandRegistry"]);
        super(rest);
        this.options = options;
        this._backendCheck = backendCheck;
        this._commands = options.commands;
        this._externalCommandRegistry = externalCommandRegistry;
        this._contentsManager = (_a = options.manager) === null || _a === void 0 ? void 0 : _a.contents;
    }
    /**
     * Create a new widget given a context.
     *
     * @param context Contains the information of the file
     * @returns The widget
     */
    createNewWidget(context) {
        if (this._backendCheck) {
            const checked = this._backendCheck();
            if (!checked) {
                throw new Error('Requested backend is not installed');
            }
        }
        const { model } = context;
        model.filePath = context.localPath;
        context.pathChanged.connect(() => {
            model.filePath = context.localPath;
        });
        if (this._contentsManager) {
            model.contentsManager = this._contentsManager;
        }
        const content = new JupyterGISPanel({
            model,
            manager: this.options.manager,
            contentFactory: this.options.contentFactory,
            mimeTypeService: this.options.mimeTypeService,
            rendermime: this.options.rendermime,
            consoleTracker: this.options.consoleTracker,
            commandRegistry: this.options.commands,
            state: this.options.state,
            formSchemaRegistry: this.options.formSchemaRegistry,
            annotationModel: this.options.annotationModel,
        });
        const toolbar = new ToolbarWidget({
            commands: this._commands,
            model,
            externalCommands: this._externalCommandRegistry.getCommands(),
        });
        return new JupyterGISDocumentWidget({
            context,
            content,
            toolbar,
        });
    }
}
