import re
from robot.variables import is_var
from PySide.QtCore import Qt
from PySide.QtGui import (QTextEdit, QTextDocument, QCompleter,
        QTextCursor, QTextCharFormat, QColor, QBrush, QLabel,
        QSyntaxHighlighter)


class RobotDataEditor(QTextEdit):

    def __init__(self, data):
        super(RobotDataEditor, self).__init__()
        self._completer = SettingNameCompleter(self)
        self._completer.activated.connect(self._completion)
        self._data = data
        self.setDocument(QTextDocument(self._data.content))
        self.setMouseTracking(True)
        self._mouse_position = None
        self._link = None
        self._help = None

    @property
    def path(self):
        return self._data.path

    @property
    def content(self):
        return self.document().toPlainText()

    @property
    def is_modified(self):
        return self.document().isModified()

    def save(self):
        self._data.save(self.content)
        self.document().setModified(False)

    def _text_under_cursor(self):
        tc = self.textCursor()
        tc.select(QTextCursor.WordUnderCursor)
        return tc.selectedText()

    def mouseMoveEvent(self, event):
        self._mouse_position = event.pos()

    def keyPressEvent(self, event):
        if self._ignorable(event):
            event.ignore()
            return
        if self._requests_completion(event):
            self._completer.show_completion_for(self._text_under_cursor(),
                    self.cursorRect())
        elif self._requests_info(event):
            self._show_info()
        QTextEdit.keyPressEvent(self, event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Control and self._link:
            self._link.setCharFormat(QTextCharFormat())
        if event.key() == Qt.Key_Control and self._help:
            self._help.hide()

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

    def _requests_info(self, event):
        return event.key() == Qt.Key_Control

    def _show_info(self):
        self._link = self._create_info_cursor()
        self._help = self._create_help_display()

    def _create_info_cursor(self):
        cursor = self.cursorForPosition(self._mouse_position)
        cursor.select(QTextCursor.WordUnderCursor)
        format = QTextCharFormat()
        format.setFontUnderline(True)
        format.setForeground(QBrush(QColor('blue')))
        cursor.setCharFormat(format)
        return cursor

    def _create_help_display(self):
        label = QLabel(self)
        label.setText('<b>this is doc</b>'
            '<table><tr><td>Example:</td><td>value</td></tr></table>')
        label.setStyleSheet("QLabel {background-color: yellow}")
        label.move(self._mouse_position)
        label.show()
        return label


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


def create_table_matcher(name):
    return re.compile('\*+\W*(%s|%ss)\W*\*+' % (name, name), re.I)


class RobotHiglighter(QSyntaxHighlighter):
    _tables = [create_table_matcher(name) for name in
            ('setting', 'variable', 'test case', 'keyword')]

    def __init__(self, parent):
        super(RobotHiglighter, self).__init__(parent)
        self._current_table = 0

    def highlightBlock(self, text):
        hl = self._highlighter(text)
        self.setFormat(hl.start, hl.end, hl.style)

    def _highlighter(self, text):
        match = self._match_header(text)
        if match:
            return Highlighter(match.start(), match.end(), TableHeaderStyle())
        return {
            1: SettingRowHighlighter,
            2: VariableRowHighlighter,
            }.get(self.current, NoHighlighter)(text)

    def _match_header(self, line):
        for index, table in enumerate(self._tables):
            match = table.match(line)
            if match:
                self.current = index + 1
                return match


class Highlighter(object):

    def __init__(self, start, end, style):
        self.start = start
        self.end = end
        self.style = style


class SettingRowHighlighter(object):

    def __init__(self, text):
        self.start = 0
        self.end = text.index(' ') if ' ' in text else 0
        self.style = SyntaxElementStyle()


class VariableRowHighlighter(object):

    def __init__(self, text):
        self.start, self.end = self._get_veriable_position(text)
        self.style = VariableNameStyle()

    def _get_veriable_position(self, text):
        if text:
            name = text.split()[0]
            if is_var(name):
                return 0, len(name)
        return 0, 0


class NoHighlighter(object):

    def __init__(self, text):
        self.start = 0
        self.end = 0
        self.style = None


class SyntaxElementStyle(QTextCharFormat):

    def __init__(self):
        super(SyntaxElementStyle, self).__init__()
        self.setForeground(Qt.darkCyan)


class TableHeaderStyle(QTextCharFormat):

    def __init__(self):
        super(TableHeaderStyle, self).__init__()
        self.setForeground(Qt.darkMagenta)


class VariableNameStyle(QTextCharFormat):
    def __init__(self):
        super(VariableNameStyle, self).__init__()
        self.setForeground(Qt.darkYellow)
