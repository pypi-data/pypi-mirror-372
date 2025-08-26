import os
import pathlib
import sys
import enum
import typing
import webbrowser
import traceback
from PySide6 import QtGui
from PySide6.QtCore import QFile, QRegularExpression, Qt, Signal
from PySide6.QtGui import (
    QBrush,
    QIcon,
    QRegularExpressionValidator,
    QPalette,
    QColorConstants,
)
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QTableWidgetItem,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from itchi.gui.controller import Controller, EConfigSectionAttributeType, ConfigSectionAttribute


class CmdSelectionQComboBox(QComboBox):
    currentCmdChanged = Signal(str, str)

    def __init__(self):
        super().__init__()
        self.prevIndex = 0
        self.currentIndexChanged.connect(self.currentIndexChangedHandler)

    def currentIndexChangedHandler(self, currentIndex):
        if currentIndex != self.prevIndex:
            prevCmd = self.itemText(self.prevIndex)
            currentCmd = self.itemText(currentIndex)

            self.prevIndex = currentIndex
            self.currentCmdChanged.emit(prevCmd, currentCmd)


class CmdSelectionGroupQTreeWidgetItem(QTreeWidgetItem):
    def __init__(
        self,
        parent: QTreeWidgetItem,
        groupName: str,
        cmds: typing.Iterable,
        selectedCmdChangedCallback,
    ):
        super().__init__(parent, [groupName])
        self._selectedCmdChangedCallback = selectedCmdChangedCallback

        self._checkStatePrev = Qt.CheckState.Unchecked
        self.setCheckState(0, Qt.CheckState.Unchecked)
        self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)  # type: ignore

        cmdQCB = CmdSelectionQComboBox()
        for cmd in cmds:
            cmdQCB.addItem(cmd)

        # Disable QTreeWidgetItem if the combobox is empty
        if cmdQCB.count() == 0:
            self.setDisabled(True)

        self.treeWidget().setItemWidget(self, 1, cmdQCB)

        cmdQCB.currentCmdChanged.connect(self.groupCmdChangedHandler)

    def itemChangedHandler(self):
        checkStateNow = self.checkState(0)
        if checkStateNow != self._checkStatePrev:
            self._checkStatePrev = checkStateNow

            cmdKey = self.treeWidget().itemWidget(self, 1).currentText()
            self._selectedCmdChangedCallback(cmdKey)

    def groupCmdChangedHandler(self, prevCmd: str, currentCmd: str):
        checkStateNow = self.checkState(0)
        if checkStateNow == Qt.CheckState.Checked:
            self._selectedCmdChangedCallback(prevCmd)
            self._selectedCmdChangedCallback(currentCmd)
        else:
            self._selectedCmdChangedCallback(currentCmd)


class CPropertyEditorQTreeWidget(QTreeWidget):
    class CBooleanQTreeWidgetItem(QTreeWidgetItem):
        def __init__(self, parent: QTreeWidgetItem, propertyName: str, value: bool) -> None:
            super().__init__(parent, [propertyName, ""])
            self.setCheckState(
                1, Qt.CheckState.Checked if value is True else Qt.CheckState.Unchecked
            )
            self.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)  # type: ignore

        def text(self, column: int) -> str:
            if column == 1:
                if self.checkState(column) == Qt.CheckState.Checked:
                    return "True"
                else:
                    return "False"

            return super().text(column)

    class CComboQTreeWidgetItem(QTreeWidgetItem):
        def __init__(self, parent: QTreeWidgetItem, propertyName: str, value: enum.Enum):
            super().__init__(parent, [propertyName, ""], type=EConfigSectionAttributeType.Enum)

            layout = QHBoxLayout()
            self.comboBox = QComboBox()
            activeItem = value
            self.comboBox.addItem(activeItem.value)
            for item in type(activeItem):
                if item != activeItem:
                    self.comboBox.addItem(item.value)
            layout.setContentsMargins(2, 1, 5, 1)
            layout.addWidget(self.comboBox, alignment=Qt.AlignmentFlag.AlignLeft)
            newWidget = QWidget()
            newWidget.setLayout(layout)
            self.treeWidget().setItemWidget(self, 1, newWidget)
            self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # type: ignore

        def text(self, column) -> str:
            if column == 1:
                text = self.comboBox.currentText()
            else:
                text = super().text(column)
            return text

    class CPathQTreeWidgetItem(QTreeWidgetItem):
        def __init__(self, parent: QTreeWidgetItem, propertyName: str, value: str):
            super().__init__(parent, [propertyName, ""], type=EConfigSectionAttributeType.Path)

            layout = QHBoxLayout()
            layout.setContentsMargins(5, 1, 5, 1)

            self.label = QLabel(value)
            layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignLeft)

            toolButton = QToolButton()
            toolButton.setText("...")
            toolButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
            toolButton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
            toolButton.setFixedSize(40, 20)

            selectFileMenu = QMenu(toolButton)
            selectFileMenu.addAction(
                "Absolute...",
                self.getToolButtonSmartSelectClickedHandler(absolute=True, property=propertyName),
            )
            toolButton.setMenu(selectFileMenu)

            layout.addWidget(toolButton, alignment=Qt.AlignmentFlag.AlignRight)
            toolButton.clicked.connect(
                self.getToolButtonSmartSelectClickedHandler(absolute=False, property=propertyName)
            )

            newWidget = QWidget()
            newWidget.setLayout(layout)
            self.treeWidget().setItemWidget(self, 1, newWidget)

            self.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # type: ignore

        def editItem(self, column: int) -> None:
            if column != 1:
                return

            # Get current text and hide the label; Create new lineEdit so user can modify path;
            # Connect editingFinished signal to custom handler; Insert the lineEdit in current
            # treeWidgetItem
            currentText = self.label.text()
            self.label.hide()

            # (Workaround) add one empty char and immediately delete it so that
            # editingFinished will be emitted even when nothing changes
            lineEdit = QLineEdit(currentText + " ")
            lineEdit.backspace()
            lineEdit.editingFinished.connect(self.lineEditEditingFinishedHandler)

            itemWidget = self.treeWidget().itemWidget(self, 1).layout()
            itemWidget.layout().insertWidget(0, lineEdit)
            lineEdit.setFocus()

        def lineEditEditingFinishedHandler(self):
            # Get new path from lineEdit, delete it and set the new path to label
            itemWidget = self.treeWidget().itemWidget(self, 1)
            lineEdit = itemWidget.layout().takeAt(0).widget()
            newText = lineEdit.text()
            lineEdit.deleteLater()

            self.label = itemWidget.layout().itemAt(0).widget()
            self.label.setText(newText)
            self.label.show()

        def getToolButtonSmartSelectClickedHandler(self, absolute=False, property=""):
            def toolButtonSmartSelectClickedHandler():
                if property in saveFileMapping:
                    name = saveFileMapping[property]
                    filename, _ = QFileDialog.getSaveFileName(
                        caption=f"Save file {name}", dir=name, filter="*"
                    )
                else:
                    filename, _ = QFileDialog.getOpenFileName(
                        caption=f"Select file for {property}", dir="", filter="*"
                    )
                if filename and absolute is False:
                    try:
                        filePath = pathlib.Path(filename)
                        filePath = pathlib.Path.relative_to(filePath, pathlib.Path.cwd())
                    except BaseException:
                        filePath = filename
                    self.label.setText(str(filePath))
                elif filename:
                    self.label.setText(str(filename))

            saveFileMapping = {
                "vector_os_timing_hooks_h": "Os_TimingHooks_winidea.h",
                "vector_os_timing_hooks_c": "Os_TimingHooks_winidea.c",
                "impl_vfb_hooks_c": "vfb_hooks_winidea.c",
            }
            return toolButtonSmartSelectClickedHandler

        def text(self, column) -> str:
            if column == 1:
                text = self.label.text()
            else:
                text = super().text(column)

            return text

    class CIterableOneColumnQTreeWidgetItem(QTreeWidgetItem):
        def __init__(self, parent: QTreeWidgetItem, value: str):
            self._parent = parent
            QTreeWidgetItem.__init__(
                self,
                self._parent,
                [str(self._parent.childCount()), value],
                type=EConfigSectionAttributeType.IterableOneColumn,
            )
            self.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # type: ignore
            self._updateParentValueView()

        def setData(self, column: int, role: int, value: typing.Any) -> None:
            super().setData(column, role, value)

            # For column 0 only program can set data, so we don't need to update parent or
            # add/remove elements as only item indexes have changed
            if column == 0:
                return

            numItems = self._parent.childCount()
            selfIdx = self._parent.indexOfChild(self)

            if value:
                # If value was set to the last item in the list, add new item to the end (new line)
                if selfIdx == numItems - 1:
                    CPropertyEditorQTreeWidget.CIterableOneColumnQTreeWidgetItem(self._parent, "")
            else:
                # Delete the item if it isn't the last one in the list
                if (numItems > 1) and (selfIdx != numItems - 1):
                    self._parent.removeChild(self)
                    for childIdx in range(selfIdx, self._parent.childCount()):
                        self._parent.child(childIdx).setText(0, str(childIdx))

            self._updateParentValueView()

        def _updateParentValueView(self):
            parentValue = ""
            for childIdx in range(self._parent.childCount() - 1):
                parentValue += f"'{self._parent.child(childIdx).text(1)}', "

            self._parent.setText(1, parentValue[0:-2])

    class CIterableTwoColumnsQTreeWidgetItem(QTreeWidgetItem):
        _placeholdertext = "Set text here"

        def __init__(self, parent: QTreeWidgetItem, valueCol0: str, valueCol1: str):
            self._parent = parent
            QTreeWidgetItem.__init__(
                self,
                self._parent,
                [valueCol0, valueCol1],
                type=EConfigSectionAttributeType.IterableTwoColumns,
            )
            if (not valueCol0) and (not valueCol1):
                # Set placholder text in each cell if there is no initial value specified
                super().setData(0, Qt.ItemDataRole.EditRole, self._placeholdertext)
                super().setData(1, Qt.ItemDataRole.EditRole, self._placeholdertext)
                super().setData(0, Qt.ItemDataRole.ForegroundRole, QBrush(Qt.GlobalColor.gray))
                super().setData(1, Qt.ItemDataRole.ForegroundRole, QBrush(Qt.GlobalColor.gray))
            self.setFlags(Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsEnabled)  # type: ignore
            self._updateParentValueView()

        def setData(self, column: int, role: int, value: typing.Any) -> None:
            if value == self._placeholdertext:
                return

            super().setData(column, role, value)
            super().setData(column, Qt.ItemDataRole.ForegroundRole, QBrush(Qt.GlobalColor.black))

            numItems = self._parent.childCount()
            selfIdx = self._parent.indexOfChild(self)

            if value:
                # If value was set to the last item in the list, add new item to the end (new line)
                if selfIdx == numItems - 1:
                    CPropertyEditorQTreeWidget.CIterableTwoColumnsQTreeWidgetItem(
                        self._parent, "", ""
                    )
            else:
                # Check if the other column is also empty and if this is not the last item in the
                # list, delete it
                if not self.text(0 if column == 1 else 1):
                    if (numItems > 1) and (selfIdx != numItems - 1):
                        self._parent.removeChild(self)

            self._updateParentValueView()

        def _updateParentValueView(self):
            parentValue = ""
            for childIdx in range(self._parent.childCount() - 1):
                # (Workaround) When one of the values in item changes role, they're both updated so
                # there is no way to differentiate between regular and placholder text at this point
                # (other than comparing the text)
                valueCol1 = self._parent.child(childIdx).text(0)
                valueCol2 = self._parent.child(childIdx).text(1)
                valueCol1 = valueCol1 if valueCol1 != self._placeholdertext else ""
                valueCol2 = valueCol2 if valueCol2 != self._placeholdertext else ""
                parentValue += f"'{valueCol1}': '{valueCol2}', "

            self._parent.setText(1, parentValue[0:-2])

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # QTreeWidget.__init__(self, parent)
        self.setHeaderHidden(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.setColumnCount(2)
        self.setIndentation(10)

        self.setStyleSheet(
            "QTreeView {"
            "show-decoration-selected: 1;"
            "}"
            "QTreeView::item {"
            "height: 25px;"
            "border: 1px solid #d9d9d9;"
            "border-top-color: transparent;"
            "border-bottom-color: transparent;"
            "}"
            "QTreeView::item:hover {"
            "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #e7effd, stop: 1 #cbdaf1);"
            "border: 1px solid #bfcde4;"
            "}"
            "QTreeView::item:selected {"
            "border: 1px solid #567dbc;"
            "}"
            "QTreeView::item:selected:active{"
            "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6ea1f1, stop: 1 #567dbc);"
            "}"
            "QTreeView::item:selected:!active {"
            "background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #6b9be8, stop: 1 #577fbf);"
            "}"
        )
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.itemDoubleClicked.connect(self.itemDoubleClickedHandler)

    def drawRow(self, painter, option, index):
        # Color only top level items
        if index.parent().isValid() is False:
            painter.save()
            painter.fillRect(option.rect, Qt.gray)
            painter.restore()
        QTreeWidget.drawRow(self, painter, option, index)

    def itemDoubleClickedHandler(self, item, column):
        if isinstance(item, self.CPathQTreeWidgetItem):
            item.editItem(column)
            return True
        elif (
            (isinstance(item, QTreeWidgetItem) and column == 1)
            or (isinstance(item, self.CIterableOneColumnQTreeWidgetItem) and column == 1)
            or isinstance(item, self.CIterableTwoColumnsQTreeWidgetItem)
        ):
            self.editItem(item, column)

    def addConfigSection(self, configSection: str):
        # Check if subsection was already added and enable it or create a new one
        foundItemsQList = self.findItems(configSection, Qt.MatchFlag.MatchExactly, 0)
        if foundItemsQList:
            for configSectionItem in foundItemsQList:
                configSectionItem.setHidden(False)
        else:
            configSectionItem = QTreeWidgetItem([configSection])
            self.addTopLevelItem(configSectionItem)
            configSectionItem.setFirstColumnSpanned(True)

    def addProperty(self, configSection: str, attribute: ConfigSectionAttribute):
        configSectionItem: QTreeWidgetItem = self.findItems(
            configSection, Qt.MatchFlag.MatchExactly, 0
        )[0]

        # Config section already contains a property with the same name -> skip adding another one
        for propertyIdx in range(configSectionItem.childCount()):
            if configSectionItem.child(propertyIdx).text(0) == attribute.name:
                return

        if attribute.type == EConfigSectionAttributeType.Boolean:
            valueBool = True if attribute.value is True else False
            propertyItem = CPropertyEditorQTreeWidget.CBooleanQTreeWidgetItem(
                configSectionItem, attribute.name, valueBool
            )
        elif attribute.type == EConfigSectionAttributeType.Enum:
            propertyItem = CPropertyEditorQTreeWidget.CComboQTreeWidgetItem(
                configSectionItem, attribute.name, attribute.value
            )
        elif attribute.type == EConfigSectionAttributeType.Path:
            value = "" if attribute.value is None else str(attribute.value)
            propertyItem = CPropertyEditorQTreeWidget.CPathQTreeWidgetItem(
                configSectionItem, attribute.name, value
            )
        elif attribute.type == EConfigSectionAttributeType.IterableOneColumn:
            valuesList = [] if not attribute.value else attribute.value
            # Create new expandable item and populate its value items
            # Add another empty item at the end for user input
            propertyItem = QTreeWidgetItem([attribute.name, ""])
            for value in valuesList:
                CPropertyEditorQTreeWidget.CIterableOneColumnQTreeWidgetItem(
                    propertyItem, str(value)
                )
            CPropertyEditorQTreeWidget.CIterableOneColumnQTreeWidgetItem(propertyItem, "")
        elif attribute.type == EConfigSectionAttributeType.IterableTwoColumns:
            valuesList = [] if not attribute.value else list(attribute.value)

            # Create new expandable item and populate its value items
            # Add another empty item at the end for user input
            propertyItem = QTreeWidgetItem([attribute.name, ""])
            for values in valuesList:
                CPropertyEditorQTreeWidget.CIterableTwoColumnsQTreeWidgetItem(
                    propertyItem, str(values[0]), str(values[1])
                )
            CPropertyEditorQTreeWidget.CIterableTwoColumnsQTreeWidgetItem(propertyItem, "", "")
        else:
            value = "" if attribute.value is None else str(attribute.value)
            propertyItem = QTreeWidgetItem([attribute.name, value])
            propertyItem.setFlags(
                Qt.ItemFlag.ItemIsEditable
                | Qt.ItemFlag.ItemIsSelectable
                | Qt.ItemFlag.ItemIsEnabled
            )

        configSectionItem.addChild(propertyItem)


class MainUI(QMainWindow):
    def __init__(self, uiWindow, configFilePath=None):
        super(MainUI, self).__init__()

        self.controller = None

        self.ui = uiWindow
        icon_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "gui", "icon.png"))
        self.ui.setWindowIcon(QIcon(icon_path))

        self.ui.groupBox_ortiPxml.setEnabled(False)
        self.ui.groupBox_commands.setEnabled(False)

        # Group box for ORTI and Profiler XML file paths configuration
        self.ui.lineEdit_ortiFilePath.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r"^.+\.(?:[oO][rR][tT][iI]?)$"), self.ui.lineEdit_ortiFilePath
            )
        )
        self.ui.lineEdit_ortiFilePath.textChanged.connect(
            self.lineEdit_ortiFilePath_textChangedHandler
        )

        self.ui.lineEdit_pxmlFilePath.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r"^.+\.(?:[xX][mM][lL])$"), self.ui.lineEdit_ortiFilePath
            )
        )
        self.ui.lineEdit_pxmlFilePath.textChanged.connect(
            self.lineEdit_pxmlFilePath_textChangedHandler
        )

        self.ui.toolButton_ortiFilePath_Menu = QMenu(self.ui.toolButton_ortiFilePath_Open)
        self.ui.toolButton_ortiFilePath_Menu.addAction(
            "Absolute path...", self.toolButton_ortiFilePath_OpenAbsolute_clickedHandler
        )
        self.ui.toolButton_ortiFilePath_Open.setMenu(self.ui.toolButton_ortiFilePath_Menu)
        self.ui.toolButton_ortiFilePath_Open.clicked.connect(
            self.toolButton_ortiFilePath_Open_clickedHandler
        )

        self.ui.toolButton_pxmlFilePath_Menu = QMenu(self.ui.toolButton_pxmlFilePath_SaveAs)
        self.ui.toolButton_pxmlFilePath_Menu.addAction(
            "Absolute path...", self.toolButton_pxmlFilePath_SaveAsAbsolute_clickedHandler
        )
        self.ui.toolButton_pxmlFilePath_SaveAs.setMenu(self.ui.toolButton_pxmlFilePath_Menu)
        self.ui.toolButton_pxmlFilePath_SaveAs.clicked.connect(
            self.toolButton_pxmlFilePath_SaveAs_clickedHandler
        )

        # Group box for JSON file path configuration
        self.ui.lineEdit_jsonFilePath.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r"^.+\.json$"), self.ui.lineEdit_jsonFilePath
            )
        )
        self.ui.lineEdit_jsonFilePath.textChanged.connect(
            self.lineEdit_jsonFilePath_textChangedHandler
        )

        self.ui.pushButton_jsonFilePath_OpenCreate.clicked.connect(
            self.pushButton_jsonFilePath_OpenCreate_clickedHandler
        )

        # Group box for command selection and help display
        self.ui.treeWidget_cmdSelection.setColumnCount(2)
        self.ui.treeWidget_cmdSelection.currentItemChanged.connect(
            self.treeWidget_cmdSelection_currentItemChangedHandler
        )
        self.ui.treeWidget_cmdSelection.itemChanged.connect(
            self.treeWidget_cmdSelection_itemChangedHandler
        )

        # Replace propertyEditor with custom QWidget to handle data better
        treeWidget_propertyEditor_layout = self.ui.treeWidget_propertyEditor.parent().layout()
        treeWidget_propertyEditor_custom = CPropertyEditorQTreeWidget()
        treeWidget_propertyEditor_layout.replaceWidget(
            self.ui.treeWidget_propertyEditor, treeWidget_propertyEditor_custom
        )
        self.ui.treeWidget_propertyEditor.deleteLater()
        self.ui.treeWidget_propertyEditor = treeWidget_propertyEditor_custom

        # Help
        self.ui.pushButton_help.clicked.connect(self.pushButton_help_clickedHandler)
        self.ui.pushButton_help.setShortcut(QtGui.QKeySequence.StandardKey.HelpContents)

        # Page navigation buttons
        self.ui.pushButton_cancel.clicked.connect(self.pushButton_cancel_clickedHandler)
        self.ui.pushButton_back.clicked.connect(self.pushButton_back_clickedHandler)
        self.ui.pushButton_next.clicked.connect(self.pushButton_next_clickedHandler)
        self.ui.pushButton_next.setEnabled(False)

        self.ui.stackedWidget.currentChanged.connect(self.stackedWidget_currentChangedHandler)
        self.ui.stackedWidget.setCurrentWidget(self.ui.firstPage)

        # Connect attribute help table with the attribute's property editor
        self.ui.treeWidget_propertyEditor.currentItemChanged.connect(
            self.treeWidget_propertyEditor_currentItemChangedHandler
        )

        self.ui.show()
        self.ui.activateWindow()

        # Error message labels for various line edits (can't get widgets position, size, ... before
        # they are shown and move won't work correctly)
        self.ui.label_jsonFilePath_errMsg = self._createErrMsgLabel(
            self.ui.groupBox_itchi, self.ui.lineEdit_jsonFilePath
        )
        self.ui.label_ortiFilePath_errMsg = self._createErrMsgLabel(
            self.ui.groupBox_ortiPxml, self.ui.lineEdit_ortiFilePath
        )
        self.ui.label_pxmlFilePath_errMsg = self._createErrMsgLabel(
            self.ui.groupBox_ortiPxml, self.ui.lineEdit_pxmlFilePath
        )

        # Check if command help is available and initialize text browser
        htmlData = Controller.getHtmlData()
        if htmlData is None:
            htmlUrl = Controller.getHtmlUrl()
            messageBox = QMessageBox(
                QMessageBox.Icon.Warning, "Warning", "", QMessageBox.StandardButton.Close, self
            )
            messageBox.setText(
                "Error: Unable to retrieve the iTCHi help HTML page. "
                + "Please check your internet connection and try again.\n"
                + f"Expected url is: {htmlUrl}\n\n"
                + "No help will be shown for the selected commands."
            )
            messageBox.exec()
        else:
            self.ui.textBrowser_cmdHelp.setHtml(htmlData)
            self.ui.textBrowser_cmdHelp.setOpenLinks(False)
            self.ui.textBrowser_cmdHelp.setOpenExternalLinks(False)
            self.ui.textBrowser_cmdHelp.scrollToAnchor("runningtaskisr")

        # Open or create config file that was passed as an argument
        if configFilePath is not None:
            configFilePath = pathlib.Path(configFilePath)
            self.pushButton_jsonFilePath_OpenCreate_clickedHandler(False, str(configFilePath))

    def _createErrMsgLabel(self, parent: QGroupBox, associatedLabel: QLabel):
        label_errMsg = QLabel(parent)
        label_errMsg.setStyleSheet("color: red")
        label_errMsg.hide()

        label_errMsg.move(associatedLabel.mapToParent(associatedLabel.rect().bottomLeft()))

        return label_errMsg

    def _setClearErrMsgLabel(
        self, associatedLineEdit: QLineEdit, errLabel: QLabel, errLabelMsg: str = ""
    ):
        if errLabelMsg:
            associatedLineEdit.setStyleSheet("QLineEdit{border: 2px solid red}")
            errLabel.setText(errLabelMsg)
            errLabel.adjustSize()
            errLabel.show()
        else:
            associatedLineEdit.setStyleSheet("")
            errLabel.hide()

    def lineEdit_jsonFilePath_textChangedHandler(self, configFilePath: str):
        self.ui.groupBox_ortiPxml.setEnabled(False)
        self.ui.groupBox_commands.setEnabled(False)
        self.ui.pushButton_next.setEnabled(False)

        self._setClearErrMsgLabel(self.ui.lineEdit_ortiFilePath, self.ui.label_ortiFilePath_errMsg)
        self._setClearErrMsgLabel(self.ui.lineEdit_pxmlFilePath, self.ui.label_pxmlFilePath_errMsg)

        if self.ui.lineEdit_jsonFilePath.hasAcceptableInput():
            self.controller = Controller(configFilePath)

            if self.controller.isConfigDataValid():
                # Populate commands selection tree and clear property editor's previously set
                # attributes values
                self.ui.treeWidget_cmdSelection.clear()
                self._treeWidget_cmdSelection_populate()
                self.ui.treeWidget_propertyEditor.clear()

                # Config data sucessfully loaded -> user can now edit orti and pxml file paths
                self._setClearErrMsgLabel(
                    self.ui.lineEdit_jsonFilePath, self.ui.label_jsonFilePath_errMsg
                )
                self.ui.groupBox_ortiPxml.setEnabled(True)

                self.ui.lineEdit_ortiFilePath.setText(" ")
                self.ui.lineEdit_pxmlFilePath.setText(" ")

                # Load path to orti file and profiler XML from config file
                ortiFilePath = self.controller.getOrtiFilePath()
                self.ui.lineEdit_ortiFilePath.setText(ortiFilePath)

                pxmlFilePath = self.controller.getPxmlFilePath()
                self.ui.lineEdit_pxmlFilePath.setText(str(pxmlFilePath))

            else:
                self._setClearErrMsgLabel(
                    self.ui.lineEdit_jsonFilePath,
                    self.ui.label_jsonFilePath_errMsg,
                    "File not found or there was an error while parsing data from it. Try creating a new one by selecting Create option",
                )

        else:
            self._setClearErrMsgLabel(
                self.ui.lineEdit_jsonFilePath,
                self.ui.label_jsonFilePath_errMsg,
                "Invalid file path. Expected *.json",
            )

    def pushButton_jsonFilePath_OpenCreate_clickedHandler(
        self, checked: bool = False, configFilePath: typing.Optional[str] = None
    ):
        _ = checked

        if configFilePath is None:
            dialog = QFileDialog(self, "Open or Create new JSON configuration file")
            dialog.setNameFilter("JSON File (*.json)")
            dialog.setFileMode(QFileDialog.FileMode.AnyFile)
            dialog.setViewMode(QFileDialog.ViewMode.Detail)
            dialog.setLabelText(QFileDialog.Accept, "Open/Create")

            if dialog.exec():
                configFilePath = dialog.selectedFiles()[0]

                if configFilePath and not pathlib.Path(configFilePath).suffix:
                    configFilePath = f"{configFilePath}.json"

        # Do not override text when no file was specified
        if configFilePath is None:
            return

        if (
            not pathlib.Path(configFilePath).exists()
            and pathlib.Path(configFilePath).suffix == ".json"
        ):
            Controller.createDefaultConfigFile(configFilePath)

        # (Workaround) For validator to accept the same name and check it again
        self.ui.lineEdit_jsonFilePath.setText("")  # (Workaround)
        self.ui.lineEdit_jsonFilePath.setText(configFilePath)

    def _ortiPxmlFileLoaded(self):
        ortiPathValid = self.ui.label_ortiFilePath_errMsg.isHidden()
        pxmlPathValid = self.ui.label_pxmlFilePath_errMsg.isHidden()
        if ortiPathValid and pxmlPathValid:
            self.ui.groupBox_commands.setEnabled(True)
            self._treeWidget_cmdSelection_update()

    def lineEdit_ortiFilePath_textChangedHandler(self, ortiFilePath: str):
        self.ui.groupBox_commands.setEnabled(False)
        self.ui.pushButton_next.setEnabled(False)

        if self.ui.lineEdit_ortiFilePath.hasAcceptableInput():
            bSuccess = self.controller.setOrtiFilePath(ortiFilePath)

            if bSuccess:
                self._setClearErrMsgLabel(
                    self.ui.lineEdit_ortiFilePath, self.ui.label_ortiFilePath_errMsg
                )
                self._ortiPxmlFileLoaded()
            else:
                self._setClearErrMsgLabel(
                    self.ui.lineEdit_ortiFilePath,
                    self.ui.label_ortiFilePath_errMsg,
                    "File doesn't exist",
                )

        else:
            self._setClearErrMsgLabel(
                self.ui.lineEdit_ortiFilePath,
                self.ui.label_ortiFilePath_errMsg,
                "Invalid file path. Expected *.ort, *.orti, *.ORT, *.ORTI",
            )

    def lineEdit_pxmlFilePath_textChangedHandler(self, pxmlFilePath: str):
        self.ui.groupBox_commands.setEnabled(False)
        self.ui.pushButton_next.setEnabled(False)

        if self.ui.lineEdit_pxmlFilePath.hasAcceptableInput():
            bSuccess = self.controller.setPxmlFilePath(pxmlFilePath)

            if bSuccess:
                self._setClearErrMsgLabel(
                    self.ui.lineEdit_pxmlFilePath, self.ui.label_pxmlFilePath_errMsg
                )
                self._ortiPxmlFileLoaded()
            else:
                self._setClearErrMsgLabel(
                    self.ui.lineEdit_pxmlFilePath,
                    self.ui.label_pxmlFilePath_errMsg,
                    "Directory doesn't exist",
                )

        else:
            self._setClearErrMsgLabel(
                self.ui.lineEdit_pxmlFilePath,
                self.ui.label_pxmlFilePath_errMsg,
                "Invalid file path. Expected *.xml",
            )

    def toolButton_ortiFilePath_Open_clickedHandler(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open ORTI file", "", "*.ort *.orti")
        if filename:
            try:
                filePath = pathlib.Path(filename)
                filePath = pathlib.Path.relative_to(filePath, pathlib.Path.cwd())
            except BaseException:
                filePath = filename

            self.ui.lineEdit_ortiFilePath.setText(str(filePath))

    def toolButton_ortiFilePath_OpenAbsolute_clickedHandler(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open ORTI file", "", "*.ort *.orti")
        if filename:
            self.ui.lineEdit_ortiFilePath.setText(filename)

    def toolButton_pxmlFilePath_SaveAs_clickedHandler(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Profiler XML file", "profiler.xml", "*.xml"
        )
        if filename:
            try:
                filePath = pathlib.Path(filename)
                filePath = pathlib.Path.relative_to(filePath, pathlib.Path.cwd())
            except BaseException:
                filePath = filename

            self.ui.lineEdit_pxmlFilePath.setText(str(filePath))

    def toolButton_pxmlFilePath_SaveAsAbsolute_clickedHandler(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Profiler XML file", "profiler.xml", "*.xml"
        )
        if filename:
            self.ui.lineEdit_pxmlFilePath.setText(filename)

    def treeWidget_cmdSelection_currentItemChangedHandler(
        self, current: QTreeWidgetItem, previous: QTreeWidgetItem
    ):
        ##
        # @brief Handles the event when a command group is selected in treeWidget
        #
        if current is None:
            return

        # Ignore events when separator is selected
        if current.isFirstColumnSpanned():
            return

        # Ignore change events between columns
        if current != previous:
            cmdKey = current.treeWidget().itemWidget(current, 1).currentText()
            self._textEdit_cmdHelp_showCmdHelp(cmdKey)

    def treeWidget_cmdSelection_itemChangedHandler(
        self, item: CmdSelectionGroupQTreeWidgetItem, column: int
    ):
        ##
        # @brief Handles the event when the command group is checked/unchecked
        #
        _ = column

        # Ignore events when separators have changed
        if item.isFirstColumnSpanned():
            return

        item.itemChangedHandler()

    def _treeWidget_cmdSelection_groupCmdChangedCallback(self, cmdKey: str):
        ##
        # @brief Callback that handles the event between command changes inside the same group
        #
        self._treeWidget_cmdSelection_update()
        self._textEdit_cmdHelp_showCmdHelp(cmdKey)

    def _treeWidget_cmdSelection_populate(self):
        ##
        # @brief Initially populates the command selection tree widget
        #
        separatorGroupsCmds = self.controller.getGroupCmds()
        for group, cmds in separatorGroupsCmds.items():
            CmdSelectionGroupQTreeWidgetItem(
                self.ui.treeWidget_cmdSelection,
                group,
                cmds,
                self._treeWidget_cmdSelection_groupCmdChangedCallback,
            )
        self.ui.treeWidget_cmdSelection.header().setSectionResizeMode(QHeaderView.Stretch)
        self._treeWidget_cmdSelection_checkPreviouslySelectedCmds()

    def _treeWidget_cmdSelection_update(self):
        ##
        # @brief Updates the state of the `Next` button depending on whether
        #        at least one cmd is selected.
        #
        bAtLeastOneCmdChecked = any(
            self.ui.treeWidget_cmdSelection.topLevelItem(i).checkState(0) == Qt.CheckState.Checked
            for i in range(self.ui.treeWidget_cmdSelection.topLevelItemCount())
        )
        # At least one cmd has to be selected to continue to next page (enable Next button)
        self.ui.pushButton_next.setEnabled(bAtLeastOneCmdChecked)

    def _treeWidget_cmdSelection_checkPreviouslySelectedCmds(self):
        ##
        # @brief In command selection treeView (pre)select all commands that were selected in
        #        previous iteration (that are saved in config file)
        #
        for groupIdx in range(self.ui.treeWidget_cmdSelection.topLevelItemCount()):
            groupQTWI = self.ui.treeWidget_cmdSelection.topLevelItem(groupIdx)
            cmdQCB = self.ui.treeWidget_cmdSelection.itemWidget(groupQTWI, 1)
            for cmdIdx in range(cmdQCB.count()):
                cmdText = cmdQCB.itemText(cmdIdx)
                if self.controller.wasCmdPreviouslySelected(cmdText):
                    cmdQCB.setCurrentIndex(cmdIdx)
                    groupQTWI.setCheckState(0, Qt.CheckState.Checked)
                    break

    def _textEdit_cmdHelp_showCmdHelp(self, cmdKey):
        anchorId = self.controller.getHtmlElementId(cmdKey)
        self.ui.textBrowser_cmdHelp.scrollToAnchor(anchorId)

    def pushButton_help_clickedHandler(self):
        helpUrl = "https://www.isystem.com/downloads/winIDEA/help/itchi-wizard.html"
        didOpen = webbrowser.open(helpUrl, new=0, autoraise=True)

        if not didOpen:
            messageBox = QMessageBox(
                QMessageBox.Icon.Warning, "Warning", "", QMessageBox.StandardButton.Close, self
            )
            messageBox.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            messageBox.setText(
                f"Failed to open a web browser with online help located at:\n\n {helpUrl}"
            )
            messageBox.exec()

    def pushButton_cancel_clickedHandler(self):
        self.ui.close()

    def pushButton_back_clickedHandler(self):
        nextIndex = self.ui.stackedWidget.currentIndex() - 1
        self.ui.stackedWidget.setCurrentIndex(nextIndex)

    def pushButton_next_clickedHandler(self):
        nextIndex = self.ui.stackedWidget.currentIndex() + 1
        numOfWidgets = self.ui.stackedWidget.count()

        if nextIndex == numOfWidgets:
            self._pushButton_generate_clickedHandler()
        else:
            self.ui.stackedWidget.setCurrentIndex(nextIndex)

    def _pushButton_generate_clickedHandler(self):
        # Clear output window so user knows that something is in progress
        self.ui.textEdit_progress.clear()
        self.ui.textEdit_log.clear()

        # For all unhidden config section, get their attributes and set their values in config file
        for configSectionIndx in range(self.ui.treeWidget_propertyEditor.topLevelItemCount()):
            configSectionQTWI = self.ui.treeWidget_propertyEditor.topLevelItem(configSectionIndx)
            if not configSectionQTWI.isHidden():
                configSectionKey = configSectionQTWI.text(0)
                for attributeIndx in range(configSectionQTWI.childCount()):
                    attributeQTWI = configSectionQTWI.child(attributeIndx)
                    attributeKey = attributeQTWI.text(0)
                    setValue = attributeQTWI.text(1)
                    self.controller.setConfigSectionAttribute(
                        configSectionKey, attributeKey, setValue
                    )

        # Run iTCHi and show output in window
        try:
            progress_text_html = self.controller.runItchi()
        except Exception:
            exc_trace = traceback.format_exc()
            progress_text_html = f'<html><body><pre style="font-family: Consolas;color:red;">{exc_trace}<pre></body></html>'

        log_text = self.controller.getLogFileData()
        log_text_html = f"<html><body> <style>.pre {{font-family: Consolas;}}</style> <pre>{log_text}<.pre></body></html>"

        self.ui.textEdit_log.setText(log_text_html)
        self.ui.textEdit_progress.setText(progress_text_html)

        # (Workaround) Switch to "Log" tab and scroll to the bottom (otherwise scroll won't work)
        self.ui.tabWidget.setCurrentWidget(self.ui.tabWidget.findChild(QWidget, "log"))
        self.ui.textEdit_log.verticalScrollBar().setValue(
            self.ui.textEdit_log.verticalScrollBar().maximum()
        )

        self.ui.tabWidget.setCurrentWidget(self.ui.tabWidget.findChild(QWidget, "progress"))

    def stackedWidget_currentChangedHandler(self, index):
        if index == -1:
            return

        bEnableBackButton = True if index > 0 else False
        self.ui.pushButton_back.setEnabled(bEnableBackButton)

        # Set text of "Next >" button to "Generate" when on last page -> or
        # back to "Next >" when not. Similarly for "Cancel" <-> "Close"
        numOfWidgets = self.ui.stackedWidget.count()
        if index == (numOfWidgets - 1):
            self.ui.pushButton_next.setText("Generate")
            self.ui.pushButton_cancel.setText("Close")
        else:
            self.ui.pushButton_next.setText("Next >")
            self.ui.pushButton_cancel.setText("Cancel")

        # Load pages/data if necessary
        if index == 1:
            self._loadPropertyEditorPage()
            self._populateCfgAttrHelpTable()

    def _getSelectedCmds(self) -> list[str]:
        ##
        # @brief Returns a list of currently selected commands
        #
        selectedCmds = []
        for groupIdx in range(self.ui.treeWidget_cmdSelection.topLevelItemCount()):
            groupQTWI = self.ui.treeWidget_cmdSelection.topLevelItem(groupIdx)
            if groupQTWI.checkState(0) == Qt.CheckState.Checked:
                cmdQCB = self.ui.treeWidget_cmdSelection.itemWidget(groupQTWI, 1)
                selectedCmds.append(cmdQCB.currentText())
        return selectedCmds

    def _loadPropertyEditorPage(self):
        if self.controller is None:
            return

        # Get all of the selected cmds
        selectedCmds = self._getSelectedCmds()

        # Save selected commands in config file so they'll be run later when calling iTCHi exec
        self.controller.saveSelectedCommands(selectedCmds)

        # Hide already added sections (in case the cmd was unselected)
        for configSectionIndx in range(self.ui.treeWidget_propertyEditor.topLevelItemCount()):
            self.ui.treeWidget_propertyEditor.topLevelItem(configSectionIndx).setHidden(True)

        # For selected cmd get its config sections and attributes and add them to the propertyEditor
        for selectedCmd in selectedCmds:
            configSections = self.controller.getCmdConfigSections(selectedCmd)
            for configSection in configSections:
                self.ui.treeWidget_propertyEditor.addConfigSection(configSection)
                attributes = self.controller.getConfigSectionAttributes(configSection)
                for attribute in attributes:
                    self.ui.treeWidget_propertyEditor.addProperty(configSection, attribute)

    def treeWidget_propertyEditor_currentItemChangedHandler(self, item, column):
        _ = column

        if item is None:
            return

        selectedAttrFullNameStr = ""
        selectedAttrFullNameList = []
        if item.parent():
            while item:
                itemType = type(item)
                if (
                    itemType is QTreeWidgetItem
                    or itemType is CPropertyEditorQTreeWidget.CBooleanQTreeWidgetItem
                    or itemType is CPropertyEditorQTreeWidget.CPathQTreeWidgetItem
                ):
                    selectedAttrFullNameList.append(item.text(0))
                item = item.parent()

            selectedAttrFullNameList.reverse()
            selectedAttrFullNameStr = " ".join(selectedAttrFullNameList)

        if not selectedAttrFullNameStr:
            return

        if self.controller.isConfigSectionAlsoAttribute(selectedAttrFullNameList[-1]):
            if not selectedAttrFullNameList[-1]:
                return

            selectedAttrFullNameStr = selectedAttrFullNameList[-1]

        # Find the attribute's help row in the table and select it
        attrHelpItem = self.ui.tableWidget_cfgAttrHelp.findItems(
            selectedAttrFullNameStr, Qt.MatchFlag.MatchFixedString
        )
        if attrHelpItem:
            rowIdx = attrHelpItem[0].row()
            self.ui.tableWidget_cfgAttrHelp.selectRow(rowIdx)

    def _populateCfgAttrHelpTable(self):
        # Clear already populated data
        self.ui.tableWidget_cfgAttrHelp.setColumnCount(0)
        self.ui.tableWidget_cfgAttrHelp.setRowCount(0)

        # Get a list of all of the config sections that the user will be able to modify
        configSectionsList = []
        for selectedCmd in self._getSelectedCmds():
            configSectionsList += self.controller.getCmdConfigSections(selectedCmd)

        # Get help text and populate header and cell data
        namesOfColumns, cellsData = self.controller.getAttributesHelp(configSectionsList)
        for columnIdx, columnName in enumerate(namesOfColumns):
            self.ui.tableWidget_cfgAttrHelp.insertColumn(columnIdx)
            self.ui.tableWidget_cfgAttrHelp.setHorizontalHeaderItem(
                columnIdx, QTableWidgetItem(columnName)
            )

        for rowIdx, rowData in enumerate(cellsData):
            self.ui.tableWidget_cfgAttrHelp.insertRow(rowIdx)
            for cellIdx, cellData in enumerate(rowData):
                self.ui.tableWidget_cfgAttrHelp.setItem(rowIdx, cellIdx, QTableWidgetItem(cellData))

        # Resize the first column (attributes name) to fit the content
        self.ui.tableWidget_cfgAttrHelp.resizeColumnToContents(0)
        self.ui.tableWidget_cfgAttrHelp.resizeRowsToContents()


def main():
    config_file_path = None
    if len(sys.argv) > 1:
        config_file_path = str(sys.argv[1])

    ui_file_path = os.path.join(os.path.dirname(__file__), "gui", "iTCHi_Gui.ui")
    ui_file = QFile(ui_file_path)
    ui_file.open(QFile.ReadOnly)

    loader = QUiLoader()
    app = QApplication()

    app.setStyle("Fusion")
    palette = QPalette(QColorConstants.White)
    app.setPalette(palette)

    ui_window = loader.load(ui_file)
    mainUi = MainUI(ui_window, config_file_path)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
