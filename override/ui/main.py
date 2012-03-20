from __future__ import with_statement
import sys
from PySide.QtCore import Qt, QDir, QTimer
from PySide.QtGui import (QMainWindow, QTextEdit, QTextDocument, QCompleter,
        QDockWidget, QTreeView, QFileSystemModel, QApplication, QTextCursor)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self._editor = self._create_editor()
        self._navigator = self._create_navigator()
        self._decorate()
        self._save_timer = self._create_save_timer()
        self.current_file = None

    def _create_editor(self):
        editor = RobotDataEditor()
        self.setCentralWidget(editor)
        return editor

    def _create_navigator(self):
        tree = FileSystemTree(QDir.currentPath() + '/test')
        self.add_dock_widget('Navigator', tree, Qt.LeftDockWidgetArea)
        tree.clicked.connect(self.tree_item_selected)
        return tree

    def _create_save_timer(self):
        save_timer = QTimer()
        save_timer.timeout.connect(self.save)
        save_timer.start(1000)
        return save_timer

    def _decorate(self):
        self.setWindowTitle('OVERRIDE !!')
        self.setMinimumSize(800, 600)

    def tree_item_selected(self, index):
        if self._navigator.is_file(index):
            self.current_file = File(self._navigator.path(index))
            self._editor.set_content(self.current_file.content)

    def save(self):
        if self._editor.is_modified and self.current_file:
            self.current_file.save(self._editor.content)
            self._editor.set_unmodified()

    def add_dock_widget(self, title, widget, alignment):
        dock = QDockWidget(title, self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(widget)
        self.addDockWidget(alignment, dock)


class File(object):

    def __init__(self, path):
        self._path = path

    @property
    def content(self):
        return open(self._path, 'r').read()

    def save(self, new_content):
        with open(self._path, 'w') as handle:
            handle.write(new_content)


class FileSystemTree(QTreeView):

    def __init__(self, root_path):
        super(FileSystemTree, self).__init__()
        self._model = self._create_file_system_model(root_path)
        self._configure_view()

    def _create_file_system_model(self, root_path):
        model = QFileSystemModel()
        model.setRootPath(root_path)
        self.setModel(model)
        self.setRootIndex(model.index(root_path))
        return model

    def _configure_view(self):
        for i in 1, 2, 3:
            self.setColumnHidden(i, True)
        self.setHeaderHidden(True)

    def is_file(self, index):
        return not self._model.isDir(index)

    def path(self, index):
        return self._model.filePath(index)


class RobotDataEditor(QTextEdit):

    def __init__(self):
        super(RobotDataEditor, self).__init__()
        self._completer = SettingNameCompleter(self)
        self._completer.activated.connect(self._completion)

    def set_content(self, content):
        self.setDocument(QTextDocument(content))

    @property
    def content(self):
        return self.document().toPlainText()

    @property
    def is_modified(self):
        return self.document().isModified()

    def set_unmodified(self):
        self.document().setModified(False)

    def _text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def keyPressEvent(self, event):
        if self._ignorable(event):
            event.ignore()
            return
        if self._requests_completion(event):
            self._completer.show_completion_for(self._text_under_cursor(),
                    self.cursorRect())
        QTextEdit.keyPressEvent(self, event)

    def _ignorable(self, event):
        ignored = (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Escape, Qt.Key_Tab)
        return self._completer.popup().isVisible() and event.key() in ignored

    def _requests_completion(self, event):
        modifiers = [Qt.ControlModifier, Qt.ControlModifier | Qt.AltModifier]
        return event.modifiers() in modifiers and event.key() == Qt.Key_Space

    def _completion(self, completion):
        tc = self.textCursor()
        extra = len(completion) - len(self._completer.completionPrefix())
        tc.movePosition(QTextCursor.Left)
        tc.movePosition(QTextCursor.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)


class SettingNameCompleter(QCompleter):
    _setting_names = ['Documentation', 'Force Tags', 'Default Tags',
            'Suite Setup', 'Suite Teardown', 'Test Setup', 'Test Teardown',
            'Library', 'Resource', 'Variables', 'Metadata']

    def __init__(self, editor):
        super(SettingNameCompleter, self).__init__(self._setting_names)
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)
        self.setWidget(editor)

    def show_completion_for(self, prefix, position):
        self.setCompletionPrefix(prefix)
        self._show_completion_in(position)

    def _show_completion_in(self, position):
        popup = self.popup()
        position.setWidth(popup.sizeHintForColumn(0) +
                popup.verticalScrollBar().sizeHint().width())
        self.complete(position)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
