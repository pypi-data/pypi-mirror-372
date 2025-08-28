import { CommandIDs, GlobalStateDbManager, addCommands, createDefaultLayerRegistry, rasterSubMenu, vectorSubMenu, } from '@jupytergis/base';
import { IJGISFormSchemaRegistryToken, IJGISLayerBrowserRegistryToken, IJupyterGISDocTracker, ProcessingMerge, } from '@jupytergis/schema';
import { ICompletionProviderManager } from '@jupyterlab/completer';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { IStateDB } from '@jupyterlab/statedb';
import { ITranslator, nullTranslator } from '@jupyterlab/translation';
import { Menu } from '@lumino/widgets';
import { notebookRendererPlugin } from './notebookrenderer';
const plugin = {
    id: 'jupytergis:lab:main-menu',
    autoStart: true,
    requires: [
        IJupyterGISDocTracker,
        IJGISFormSchemaRegistryToken,
        IJGISLayerBrowserRegistryToken,
        IStateDB,
    ],
    optional: [IMainMenu, ITranslator, ICompletionProviderManager],
    activate: (app, tracker, formSchemaRegistry, layerBrowserRegistry, state, mainMenu, translator, completionProviderManager) => {
        console.log('jupytergis:lab:main-menu is activated!');
        translator = translator !== null && translator !== void 0 ? translator : nullTranslator;
        const isEnabled = () => {
            return (tracker.currentWidget !== null &&
                tracker.currentWidget === app.shell.currentWidget);
        };
        createDefaultLayerRegistry(layerBrowserRegistry);
        const stateDbManager = GlobalStateDbManager.getInstance();
        stateDbManager.initialize(state);
        addCommands(app, tracker, translator, formSchemaRegistry, layerBrowserRegistry, state, completionProviderManager);
        app.contextMenu.addItem({
            selector: '.jp-gis-source.jp-gis-sourceUnused',
            rank: 1,
            command: CommandIDs.removeSource,
        });
        app.contextMenu.addItem({
            selector: '.jp-gis-source',
            rank: 1,
            command: CommandIDs.renameSource,
        });
        // LAYERS and LAYER GROUPS context menu
        app.contextMenu.addItem({
            command: CommandIDs.symbology,
            selector: '.jp-gis-layerItem',
            rank: 1,
        });
        // Separator
        app.contextMenu.addItem({
            type: 'separator',
            selector: '.jp-gis-layerPanel',
            rank: 1,
        });
        app.contextMenu.addItem({
            command: CommandIDs.removeLayer,
            selector: '.jp-gis-layerItem',
            rank: 2,
        });
        app.contextMenu.addItem({
            command: CommandIDs.renameLayer,
            selector: '.jp-gis-layerItem',
            rank: 2,
        });
        app.contextMenu.addItem({
            command: CommandIDs.zoomToLayer,
            selector: '.jp-gis-layerItem',
            rank: 2,
        });
        // Create the Download submenu
        const downloadSubmenu = new Menu({ commands: app.commands });
        downloadSubmenu.title.label = translator.load('jupyterlab').__('Download');
        downloadSubmenu.id = 'jp-gis-contextmenu-download';
        downloadSubmenu.addItem({
            command: CommandIDs.downloadGeoJSON,
        });
        // Add the Download submenu to the context menu
        app.contextMenu.addItem({
            type: 'submenu',
            selector: '.jp-gis-layerItem',
            rank: 2,
            submenu: downloadSubmenu,
        });
        // Create the Processing submenu
        const processingSubmenu = new Menu({ commands: app.commands });
        processingSubmenu.title.label = translator
            .load('jupyterlab')
            .__('Processing');
        processingSubmenu.id = 'jp-gis-contextmenu-processing';
        for (const processingElement of ProcessingMerge) {
            processingSubmenu.addItem({
                command: processingElement.name,
            });
        }
        app.contextMenu.addItem({
            type: 'submenu',
            selector: '.jp-gis-layerItem',
            rank: 2,
            submenu: processingSubmenu,
        });
        const moveLayerSubmenu = new Menu({ commands: app.commands });
        moveLayerSubmenu.title.label = translator
            .load('jupyterlab')
            .__('Move Selected Layers to Group');
        moveLayerSubmenu.id = 'jp-gis-contextmenu-movelayer';
        app.contextMenu.addItem({
            type: 'submenu',
            selector: '.jp-gis-layerItem',
            rank: 2,
            submenu: moveLayerSubmenu,
        });
        app.contextMenu.opened.connect(() => buildGroupsMenu(app.contextMenu, tracker));
        app.contextMenu.addItem({
            command: CommandIDs.removeGroup,
            selector: '.jp-gis-layerGroupHeader',
            rank: 2,
        });
        app.contextMenu.addItem({
            command: CommandIDs.renameGroup,
            selector: '.jp-gis-layerGroupHeader',
            rank: 2,
        });
        // Separator
        app.contextMenu.addItem({
            type: 'separator',
            selector: '.jp-gis-layerPanel',
            rank: 2,
        });
        const newLayerSubMenu = new Menu({ commands: app.commands });
        newLayerSubMenu.title.label = translator.load('jupyterlab').__('Add Layer');
        newLayerSubMenu.id = 'jp-gis-contextmenu-addLayer';
        newLayerSubMenu.addItem({
            type: 'submenu',
            submenu: rasterSubMenu(app.commands),
        });
        newLayerSubMenu.addItem({
            type: 'submenu',
            submenu: vectorSubMenu(app.commands),
        });
        app.contextMenu.addItem({
            type: 'submenu',
            selector: '.jp-gis-layerPanel',
            rank: 3,
            submenu: newLayerSubMenu,
        });
        if (mainMenu) {
            populateMenus(mainMenu, isEnabled);
        }
    },
};
/**
 * Populates the application menus for the notebook.
 */
function populateMenus(mainMenu, isEnabled) {
    // Add undo/redo hooks to the edit menu.
    mainMenu.editMenu.undoers.redo.add({
        id: CommandIDs.redo,
        isEnabled,
    });
    mainMenu.editMenu.undoers.undo.add({
        id: CommandIDs.undo,
        isEnabled,
    });
}
/**
 * Populate submenu with current group names
 */
function buildGroupsMenu(contextMenu, tracker) {
    var _a, _b, _c, _d;
    if (!((_a = tracker.currentWidget) === null || _a === void 0 ? void 0 : _a.model)) {
        return;
    }
    const model = (_b = tracker.currentWidget) === null || _b === void 0 ? void 0 : _b.model;
    const submenu = (_d = (_c = contextMenu.menu.items.find(item => {
        var _a;
        return item.type === 'submenu' &&
            ((_a = item.submenu) === null || _a === void 0 ? void 0 : _a.id) === 'jp-gis-contextmenu-movelayer';
    })) === null || _c === void 0 ? void 0 : _c.submenu) !== null && _d !== void 0 ? _d : null;
    // Bail early if the submenu isn't found
    if (!submenu) {
        return;
    }
    submenu.clearItems();
    // need a list of group name
    const layerTree = model.getLayerTree();
    const groupNames = getLayerGroupNames(layerTree);
    function getLayerGroupNames(layerTree) {
        const result = [];
        for (const item of layerTree) {
            // Skip if the item is a layer id
            if (typeof item === 'string') {
                continue;
            }
            // Process group items
            if (item.layers) {
                result.push(item.name);
                // Recursively process the layers of the current item
                const nestedResults = getLayerGroupNames(item.layers);
                // Append the results of the recursive call to the main result array
                result.push(...nestedResults);
            }
        }
        return result;
    }
    submenu.addItem({
        command: CommandIDs.moveLayersToGroup,
        args: { label: '' },
    });
    groupNames.forEach(name => {
        submenu.addItem({
            command: CommandIDs.moveLayersToGroup,
            args: { label: name },
        });
    });
    submenu.addItem({
        command: CommandIDs.moveLayerToNewGroup,
    });
}
export default [plugin, notebookRendererPlugin];
