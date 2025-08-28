import { JupyterGISModel, } from '@jupytergis/schema';
/**
 * A Model factory to create new instances of JupyterGISModel.
 */
export class JupyterGISModelFactory {
    constructor(options) {
        /**
         * Whether the model is collaborative or not.
         */
        this.collaborative = true;
        this._disposed = false;
        this._annotationModel = options.annotationModel;
        this._settingRegistry = options.settingRegistry;
    }
    /**
     * The name of the model.
     *
     * @returns The name
     */
    get name() {
        return 'jupytergis-jgismodel';
    }
    /**
     * The content type of the file.
     *
     * @returns The content type
     */
    get contentType() {
        return 'jgis';
    }
    /**
     * The format of the file.
     *
     * @returns the file format
     */
    get fileFormat() {
        return 'text';
    }
    /**
     * Get whether the model factory has been disposed.
     *
     * @returns disposed status
     */
    get isDisposed() {
        return this._disposed;
    }
    /**
     * Dispose the model factory.
     */
    dispose() {
        this._disposed = true;
    }
    /**
     * Get the preferred language given the path on the file.
     *
     * @param path path of the file represented by this document model
     * @returns The preferred language
     */
    preferredLanguage(path) {
        return '';
    }
    /**
     * Create a new instance of JupyterGISModel.
     *
     * @returns The model
     */
    createNew(options) {
        return new JupyterGISModel({
            sharedModel: options.sharedModel,
            languagePreference: options.languagePreference,
            annotationModel: this._annotationModel,
            settingRegistry: this._settingRegistry,
        });
    }
}
