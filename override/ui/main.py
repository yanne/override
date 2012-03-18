from __future__ import with_statement
from PySide.QtCore import Qt, QDir, QTimer
from PySide.QtGui import (QMainWindow, QTextEdit, QTextDocument,
        QDockWidget, QTreeView, QFileSystemModel, QApplication)
import os
import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.editor = RobotDataEditor()
        self.setCentralWidget(self.editor)
        self.tree = FileSystemTree()
        self.add_dock_widget('Navigator', self.tree, Qt.LeftDockWidgetArea)
        self.tree.clicked.connect(self.click)
        self.setWindowTitle('OVERRIDE !!')
        self.setMinimumSize(800, 600)
        self._save_timer = self._create_save_timer()

    def click(self, index):
        if self.tree.is_file(index):
            self.current_file = self.tree.path(index)
            content = open(self.current_file, 'r').read()
            self.editor.set_content(content)

    def save(self):
        if self.editor.is_modified:
            with open(self.current_file, 'w') as outfile:
                outfile.write(self.editor.content)
            self.editor.set_unmodified()

    def add_dock_widget(self, title, widget, alignment):
        dock = QDockWidget(title, self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(widget)
        self.addDockWidget(alignment, dock)

    def _create_save_timer(self):
        save_timer = QTimer()
        save_timer.timeout.connect(self.save)
        save_timer.start(1000)
        return save_timer


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
