"""Fusion toolbar for the six optional groups in the dual-tier BoxTurtle."""
import traceback
import adsk.core
import adsk.fusion

TAB_ID = 'BoxTurtleDualTierOptionsTab'
PANEL_ID = 'BoxTurtleDualTierOptionsPanel'
COMMAND_ID = 'BoxTurtleDualTierOptionsCommand'
MARKER_GROUP = 'BoxTurtleDualTier'
MARKER_NAME = 'initialOptionVisibility'
OPTION_NAMES = (
    'Molecular sieve cassettes',
    'Hygrometer brackets',
    'Rear PTFE guides',
    'Floor seals and feedthrough plugs',
    'Anti-tip brackets',
    'Frame joints and drill template',
)
_lifetime = []
_tab = None
_definition = None
_activation_handler = None


def _get_options():
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    if not design:
        return None, None, ()
    root = design.rootComponent
    for occurrence in root.allOccurrences:
        if not occurrence.component.name.upper().startswith('OPTIONS - USE VISIBILITY'):
            continue
        detected = {}
        for item in occurrence.childOccurrences:
            prefix = item.component.name[:2]
            if prefix in {f'{n:02}' for n in range(1, len(OPTION_NAMES) + 1)}:
                detected[prefix] = item
        if len(detected) == len(OPTION_NAMES):
            return root, occurrence, tuple(detected[key] for key in sorted(detected))
    return root, None, ()


def _defaults():
    root, options, items = _get_options()
    if options and not root.attributes.itemByName(MARKER_GROUP, MARKER_NAME):
        options.isLightBulbOn = True
        for item in items:
            item.isLightBulbOn = False
        root.attributes.add(MARKER_GROUP, MARKER_NAME, 'applied')


class Activated(adsk.core.DocumentEventHandler):
    def notify(self, args):
        try:
            _defaults()
        except Exception:
            adsk.core.Application.get().log(traceback.format_exc())


class Apply(adsk.core.CommandEventHandler):
    def __init__(self, options, items):
        super().__init__()
        self.options = options
        self.items = items

    def notify(self, args):
        inputs = args.command.commandInputs
        self.options.isLightBulbOn = True
        for idx, item in enumerate(self.items):
            item.isLightBulbOn = inputs.itemById(f'option_{idx}').value


class Created(adsk.core.CommandCreatedEventHandler):
    def notify(self, args):
        _defaults()
        _, options, items = _get_options()
        if not options:
            args.command.commandInputs.addTextBoxCommandInput(
                'help', '', 'Open the dual-tier BoxTurtle STEP that contains the OPTIONS assembly.', 3, True
            )
            return
        for idx, (item, label) in enumerate(zip(items, OPTION_NAMES)):
            args.command.commandInputs.addBoolValueInput(
                f'option_{idx}', label, True, '', item.isLightBulbOn
            )
        handler = Apply(options, items)
        args.command.execute.add(handler)
        _lifetime.append(handler)


def run(context):
    global _tab, _definition, _activation_handler
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        workspace = ui.workspaces.itemById('FusionSolidEnvironment')
        _tab = workspace.toolbarTabs.itemById(TAB_ID) or workspace.toolbarTabs.add(
            TAB_ID, 'BoxTurtle Options'
        )
        panel = _tab.toolbarPanels.itemById(PANEL_ID) or _tab.toolbarPanels.add(
            PANEL_ID, 'Optional parts'
        )
        _definition = ui.commandDefinitions.itemById(COMMAND_ID) or ui.commandDefinitions.addButtonDefinition(
            COMMAND_ID, 'Show options', 'Show or hide the six optional assemblies.'
        )
        handler = Created()
        _definition.commandCreated.add(handler)
        _lifetime.append(handler)
        control = panel.controls.itemById(COMMAND_ID) or panel.controls.addCommand(_definition)
        control.isPromotedByDefault = True
        control.isPromoted = True
        _activation_handler = Activated()
        app.documentActivated.add(_activation_handler)
        _defaults()
    except Exception:
        ui.messageBox(traceback.format_exc())


def stop(context):
    app = adsk.core.Application.get()
    if _activation_handler:
        app.documentActivated.remove(_activation_handler)
    if _tab:
        _tab.deleteMe()
    if _definition:
        _definition.deleteMe()
    _lifetime.clear()
