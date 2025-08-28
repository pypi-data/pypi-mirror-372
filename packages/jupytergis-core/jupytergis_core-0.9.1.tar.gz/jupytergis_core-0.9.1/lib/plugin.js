import { AnnotationModel } from '@jupytergis/base';
import { IAnnotationToken, IJGISExternalCommandRegistryToken, IJGISFormSchemaRegistryToken, IJGISLayerBrowserRegistryToken, IJupyterGISDocTracker, } from '@jupytergis/schema';
import { WidgetTracker } from '@jupyterlab/apputils';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { ITranslator } from '@jupyterlab/translation';
import { JupyterGISExternalCommandRegistry } from './externalcommand';
import { JupyterGISLayerBrowserRegistry } from './layerBrowserRegistry';
import { JupyterGISFormSchemaRegistry } from './schemaregistry';
const NAME_SPACE = 'jupytergis';
export const trackerPlugin = {
    id: 'jupytergis:core:tracker',
    autoStart: true,
    requires: [ITranslator],
    optional: [IMainMenu],
    provides: IJupyterGISDocTracker,
    activate: (app, translator, mainMenu) => {
        const tracker = new WidgetTracker({
            namespace: NAME_SPACE,
        });
        console.log('jupytergis:core:tracker is activated!');
        return tracker;
    },
};
export const formSchemaRegistryPlugin = {
    id: 'jupytergis:core:form-schema-registry',
    autoStart: true,
    requires: [IDocumentManager],
    provides: IJGISFormSchemaRegistryToken,
    activate: (app, docmanager) => {
        const registry = new JupyterGISFormSchemaRegistry(docmanager);
        return registry;
    },
};
export const externalCommandRegistryPlugin = {
    id: 'jupytergis:core:external-command-registry',
    autoStart: true,
    requires: [],
    provides: IJGISExternalCommandRegistryToken,
    activate: (app) => {
        const registry = new JupyterGISExternalCommandRegistry();
        return registry;
    },
};
export const layerBrowserRegistryPlugin = {
    id: 'jupytergis:core:layer-browser-registry',
    autoStart: true,
    requires: [],
    provides: IJGISLayerBrowserRegistryToken,
    activate: (app) => {
        console.log('jupytergis:core:layer-browser-registry is activated');
        const registry = new JupyterGISLayerBrowserRegistry();
        return registry;
    },
};
export const annotationPlugin = {
    id: 'jupytergis:core:annotation',
    autoStart: true,
    requires: [IJupyterGISDocTracker],
    provides: IAnnotationToken,
    activate: (app, tracker) => {
        var _a;
        const annotationModel = new AnnotationModel({
            model: (_a = tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.model,
        });
        tracker.currentChanged.connect((_, changed) => {
            annotationModel.model = (changed === null || changed === void 0 ? void 0 : changed.model) || undefined;
        });
        return annotationModel;
    },
};
