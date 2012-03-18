from __future__ import with_statement
from PySide.QtCore import Qt, QDir, QTimer
from PySide.QtGui import (QMainWindow, QTextEdit, QTextDocument,
        QDockWidget, QTreeView, QFileSystemModel, QApplication)
import os
import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self._editor = self._create_editor()
        self._tree = self._create_tree()
        self._decorate()
        self._save_timer = self._create_save_timer()

    def _create_editor(self):
        editor = RobotDataEditor()
        self.setCentralWidget(editor)
        return editor

    def _create_tree(self):
        tree = FileSystemTree()
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
        if self._tree.is_file(index):
            self.current_file = File(self._tree.path(index))
            self._editor.set_content(self.current_file.content)

    def save(self):
        if self._editor.is_modified:
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

    def __init__(self):
        QTreeView.__init__(self)
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir().currentPath() + '/test')
        self.setModel(self.model)
        self.setRootIndex(self.model.index(QDir.currentPath() + '/test'))
        for i in 1,2,3:
            self.setColumnHidden(i, True)
        self.setHeaderHidden(True)

    def is_file(self, index):
        return not self.model.isDir(index)

    def path(self, index):
        return self.model.filePath(index)


class RobotDataEditor(QTextEdit):

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



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
