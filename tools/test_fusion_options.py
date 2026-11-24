#!/usr/bin/env python3
"""Smoke-test toolbar registration, visibility and cleanup without desktop Fusion."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace as Object
from zipfile import ZipFile


class Event:
    def __init__(self):
        self.handlers = []

    def add(self, handler):
        self.handlers.append(handler)

    def remove(self, handler):
        self.handlers.remove(handler)

    def fire(self, **args):
        for handler in self.handlers[:]:
            handler.notify(Object(**args))


class Collection(dict):
    def __init__(self, make):
        super().__init__()
        self.make = make

    def itemById(self, identifier):
        return self.get(identifier)

    def add(self, identifier, title):
        item = self.make(identifier, title)
        item.deleteMe = lambda: self.pop(identifier)
        self[identifier] = item
        return item

    def addCommand(self, command):
        return self.add(command.id, command.title)

    def addButtonDefinition(self, identifier, title, description):
        return self.add(identifier, title)


class Attributes(dict):
    def itemByName(self, group, key):
        return self.get((group, key))

    def add(self, group, key, value):
        self[group, key] = value


class Inputs(dict):
    def addBoolValueInput(self, key, label, checkbox, resource, value):
        assert checkbox
        self[key] = Object(label=label, value=value)

    def addTextBoxCommandInput(self, key, label, value, lines, read_only):
        assert read_only
        self[key] = Object(value=value)

    def itemById(self, key):
        return self[key]


def occurrence(name, children=()):
    return Object(component=Object(name=name), childOccurrences=children, isLightBulbOn=True)


def board():
    items = [occurrence(f"{n:02} - option") for n in range(1, 7)]
    options = occurrence("OPTIONS - use visibility to show each group", items)
    document = Object(rootComponent=Object(allOccurrences=[options], attributes=Attributes()))
    return document, options, items


def main():
    fusion_dir = Path(__file__).resolve().parents[1] / "fusion"
    with ZipFile(fusion_dir / "BoxTurtle-Fusion-Options.zip") as package:
        for filename in ("BoxTurtleOptions.py", "BoxTurtleOptions.manifest"):
            member = f"BoxTurtleOptions/{filename}"
            assert package.read(member) == (fusion_dir / member).read_bytes()

    tabs = Collection(lambda key, title: Object(
        title=title, toolbarPanels=Collection(lambda _, panel: Object(
            title=panel, controls=Collection(lambda _, control: Object(title=control))
        ))
    ))
    commands = Collection(lambda key, title: Object(id=key, title=title, commandCreated=Event()))
    ui = Object(workspaces={"FusionSolidEnvironment": Object(toolbarTabs=tabs)}, commandDefinitions=commands)
    ui.workspaces = Object(itemById=ui.workspaces.get)
    errors = []
    ui.messageBox = errors.append
    doc, options, items = board()
    app = Object(activeProduct=doc, userInterface=ui, documentActivated=Event(), log=errors.append)
    core = Object(Application=Object(get=lambda: app), DocumentEventHandler=object,
                  CommandEventHandler=object, CommandCreatedEventHandler=object)
    fusion = Object(Design=Object(cast=lambda value: value))
    fake_modules = {"adsk": Object(core=core, fusion=fusion), "adsk.core": core, "adsk.fusion": fusion}
    previous = {module: sys.modules.get(module) for module in fake_modules}
    sys.modules.update(fake_modules)
    try:
        source = fusion_dir / "BoxTurtleOptions/BoxTurtleOptions.py"
        spec = importlib.util.spec_from_file_location("BoxTurtleOptions", source)
        addon = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(addon)
        addon.run(None)

        assert not errors, errors
        assert tabs[addon.TAB_ID].title == "BoxTurtle Options"
        panel = tabs[addon.TAB_ID].toolbarPanels[addon.PANEL_ID]
        assert panel.controls[addon.COMMAND_ID].title == "Show options"
        assert panel.controls[addon.COMMAND_ID].isPromoted
        assert options.isLightBulbOn and not any(item.isLightBulbOn for item in items)

        command = Object(commandInputs=Inputs(), execute=Event())
        commands[addon.COMMAND_ID].commandCreated.fire(command=command)
        assert list(command.commandInputs) == [f"option_{n}" for n in range(6)]
        assert not any(item.value for item in command.commandInputs.values())
        command.commandInputs["option_0"].value = True
        command.commandInputs["option_3"].value = True
        command.execute.fire(command=command)
        assert [item.isLightBulbOn for item in items] == [True, False, False, True, False, False]
        app.documentActivated.fire()
        assert items[0].isLightBulbOn and items[3].isLightBulbOn

        # First use in a second document gets independent all-off defaults.
        app.activeProduct, _, second_items = board()
        app.documentActivated.fire()
        assert not any(item.isLightBulbOn for item in second_items)

        app.activeProduct = None
        command = Object(commandInputs=Inputs(), execute=Event())
        commands[addon.COMMAND_ID].commandCreated.fire(command=command)
        assert "Open the dual-tier BoxTurtle STEP" in command.commandInputs["help"].value
        assert not command.execute.handlers

        addon.stop(None)
        assert not tabs and not commands and not app.documentActivated.handlers
        assert not errors, errors
    finally:
        for key, old in previous.items():
            if old is None:
                sys.modules.pop(key, None)
            else:
                sys.modules[key] = old
    print("Fusion mock smoke test passed: ZIP matches source, toolbar, six toggles, per-design defaults, missing design, cleanup.")


if __name__ == "__main__":
    main()
