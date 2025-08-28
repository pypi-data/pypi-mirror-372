import { JupyterGISModel, } from '@jupytergis/schema';
/**
 * A Model factory to create new instances of JupyterGISModel.
 */
export class JupyterGISModelFactoryBase {
    constructor(options) {
        /**
         * Whether the model is collaborative or not.
         */
        this.collaborative = document.querySelectorAll('[data-jupyter-lite-root]')[0] === undefined;
        this._disposed = false;
        this._annotationModel = options.annotationModel;
    }
    /**
     * The name of the model.
     *
     * @returns The name
     */
    get name() {
        throw 'Not implemented';
    }
    /**
     * The content type of the file.
     *
     * @returns The content type
     */
    get contentType() {
        throw 'Not implemented';
    }
    /**
     * The format of the file.
     *
     * @returns the file format
     */
    get fileFormat() {
        return 'base64';
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
        const model = new JupyterGISModel({
            sharedModel: options.sharedModel,
            languagePreference: options.languagePreference,
            annotationModel: this._annotationModel,
            settingRegistry: this._settingRegistry,
        });
        return model;
    }
}
export class QGZModelFactory extends JupyterGISModelFactoryBase {
    /**
     * The name of the model.
     *
     * @returns The name
     */
    get name() {
        return 'jupytergis-qgzmodel';
    }
    /**
     * The content type of the file.
     *
     * @returns The content type
     */
    get contentType() {
        return 'QGZ';
    }
}
export class QGSModelFactory extends JupyterGISModelFactoryBase {
    /**
     * The name of the model.
     *
     * @returns The name
     */
    get name() {
        return 'jupytergis-qgsmodel';
    }
    /**
     * The content type of the file.
     *
     * @returns The content type
     */
    get contentType() {
        return 'QGS';
    }
}
