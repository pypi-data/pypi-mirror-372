import { IAnnotationModel, IJGISExternalCommandRegistry, IJGISFormSchemaRegistry, IJGISLayerBrowserRegistry, IJupyterGISTracker } from '@jupytergis/schema';
import { JupyterFrontEndPlugin } from '@jupyterlab/application';
export declare const trackerPlugin: JupyterFrontEndPlugin<IJupyterGISTracker>;
export declare const formSchemaRegistryPlugin: JupyterFrontEndPlugin<IJGISFormSchemaRegistry>;
export declare const externalCommandRegistryPlugin: JupyterFrontEndPlugin<IJGISExternalCommandRegistry>;
export declare const layerBrowserRegistryPlugin: JupyterFrontEndPlugin<IJGISLayerBrowserRegistry>;
export declare const annotationPlugin: JupyterFrontEndPlugin<IAnnotationModel>;
