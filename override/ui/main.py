from __future__ import with_statement
from PySide.QtCore import Qt, QDir, QTimer
from PySide.QtGui import (QMainWindow, QTextEdit, QTextDocument,
        QDockWidget, QTreeView, QFileSystemModel, QApplication)
import os
import sys


class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.textEdit = RobotDataEditor()
        self.setCentralWidget(self.textEdit)
        self.tree = FileSystemTree()
        self.add_dock_widget('Navigator', self.tree, Qt.LeftDockWidgetArea)
        self.tree.clicked.connect(self.click)
        self.setWindowTitle('OVERRIDE !!')
        self.setMinimumSize(800, 600)
        self.save_timer = QTimer()
        self.save_timer.timeout.connect(self.save)
        self.save_timer.start(1000)

    def click(self, index):
        if self.tree.is_file(index):
            self.current_file = self.tree.path(index)
            content = open(self.current_file, 'r').read()
            self.textEdit.setDocument(QTextDocument(content))

    def save(self):
        if self.textEdit.document().isModified():
            print 'saving'
            self.textEdit.document().setModified(False)
        else:
            print 'clean'

    def add_dock_widget(self, title, widget, alignment):
        dock = QDockWidget(title, self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(widget)
        self.addDockWidget(alignment, dock)


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
    pass



if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = MainWindow()
    mainWin.show()
    sys.exit(app.exec_())
