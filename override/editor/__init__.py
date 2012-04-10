from roboteditor import RobotDataEditor, RobotHiglighter


def Editor(data):
    editor = RobotDataEditor(data)
    RobotHiglighter(editor)
    return editor
