from PySide.QtGui import QTreeView, QFileSystemModel


class Navigator(QTreeView):

    def __init__(self, root_path):
        super(Navigator, self).__init__()
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

    def name(self, index):
        return self._model.fileName(index)
