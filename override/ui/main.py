from __future__ import with_statement
import sys
from PySide.QtCore import Qt, QDir, QTimer
from PySide.QtGui import QMainWindow, QDockWidget, QApplication, QTabWidget

from override.editor import Editor

from navigator import Navigator


class File(object):

    def __init__(self, path):
        self.path = path

    @property
    def content(self):
        return open(self.path, 'r').read()

    def save(self, new_content):
        with open(self.path, 'w') as handle:
            handle.write(new_content)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self._tabs = self.create_tab_widget()
        self._navigator = self._create_navigator()
        self._decorate()
        self._create_save_timer()
        self._open_files = []

    def create_tab_widget(self):
        tabs = EditorTabs()
        self.setCentralWidget(tabs)
        tabs.tabCloseRequested.connect(self._close_tab)
        return tabs

    def _create_navigator(self):
        tree = Navigator(QDir.currentPath() + '/test')
        self.add_dock_widget('Navigator', tree, Qt.LeftDockWidgetArea)
        tree.activated.connect(self.tree_item_selected)
        return tree

    def _decorate(self):
        self.setWindowTitle('OVERRIDE !!')
        self.setMinimumSize(800, 600)

    def _create_save_timer(self):
        save_timer = QTimer(self)
        save_timer.timeout.connect(self.save)
        save_timer.start(1000)

    def tree_item_selected(self, index):
        path = self._navigator.path(index)
        if path not in self._open_files and self._navigator.is_file(index):
            self._open_files.append(path)
            editor = self._create_editor(File(path))
            self._tabs.add(editor, self._navigator.name(index))

    def _close_tab(self, index):
        self._open_files.remove(self._tabs.widget(index).path)
        self._tabs.close(index)

    def _create_editor(self, data):
        return Editor(data)

    def save(self):
        editor = self._current_editor()
        if editor and editor.is_modified:
            editor.save()

    def _current_editor(self):
        return self._tabs.current

    def add_dock_widget(self, title, widget, alignment):
        dock = QDockWidget(title, self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(widget)
        self.addDockWidget(alignment, dock)


class EditorTabs(QTabWidget):

    def __init__(self):
        super(EditorTabs, self).__init__()
        self.setTabsClosable(True)

    def close(self, index):
        self.removeTab(index)

    def add(self, component, title):
        self.addTab(component, title)

    @property
    def current(self):
        return self.currentWidget()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
