from __future__ import with_statement
import sys
from PySide.QtCore import Qt, QDir, QTimer
from PySide.QtGui import QMainWindow, QDockWidget, QApplication, QTabWidget

from override.editor import RobotDataEditor

from navigator import Navigator


class File(object):

    def __init__(self, path):
        self._path = path

    @property
    def content(self):
        return open(self._path, 'r').read()

    def save(self, new_content):
        with open(self._path, 'w') as handle:
            handle.write(new_content)


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self._tabs = self.create_tab_widget()
        self._navigator = self._create_navigator()
        self._decorate()
        self._save_timer = self._create_save_timer()

    def create_tab_widget(self):
        tabs = QTabWidget()
        tabs.setTabsClosable(True)
        self.setCentralWidget(tabs)
        tabs.tabCloseRequested.connect(self._close_tab)
        return tabs

    def _close_tab(self, index):
        self._tabs.removeTab(index)

    def _create_editor(self, data):
        editor = RobotDataEditor(data)
        return editor

    def _create_navigator(self):
        tree = Navigator(QDir.currentPath() + '/test')
        self.add_dock_widget('Navigator', tree, Qt.LeftDockWidgetArea)
        tree.activated.connect(self.tree_item_selected)
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
            editor = self._create_editor(File(self._navigator.path(index)))
            self._tabs.addTab(editor, self._navigator.name(index))

    def save(self):
        editor = self._current_editor()
        if editor and editor.is_modified:
            editor.save()

    def _current_editor(self):
        return self._tabs.currentWidget()

    def add_dock_widget(self, title, widget, alignment):
        dock = QDockWidget(title, self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(widget)
        self.addDockWidget(alignment, dock)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
