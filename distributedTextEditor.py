import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from client import client
import os
from UI_package.fileSelector import Ui_fileSelector
from UI_package.createTextFile import Ui_createTextFile
from UI_package.textEditor import Ui_secondWindow


available_files = []
class mainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        global available_files
        super(mainWindow, self).__init__()

        self.ui = Ui_fileSelector()
        self.ui.setupUi(self)
        
        self.client = client("sameh")
        #load text files to the filegrid
        self.files = self.client.start()
        for f in self.files:
            if f not in available_files:
                available_files.append(f)
        self.getFiles()
        #create new file
        self.ui.newFileBtn.clicked.connect(self.createFile)

        self.show()

    def getFiles(self):
        global available_files
        ############################################################
        #### GET FILES AKA C.START() #############

        self.f = available_files
        ###########################################################
        self.filesBtn = []
        self.filesNames = []
        self.subLayout = []
        

        self.row = 0
        self.col = 0
        for i in range(len(self.f)):
            
            self.filesBtn.append(QtWidgets.QPushButton(QtGui.QIcon('./img/txt.png'),'', self))
            self.filesNames.append(QtWidgets.QLabel(self.f[i],self))

           
            self.filesBtn[i].setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
            self.filesNames[i].setAlignment(QtCore.Qt.AlignCenter)
            self.filesNames[i].setStyleSheet("font: 14px;")
            vLayout = QtWidgets.QVBoxLayout()
            vLayout.addWidget(self.filesBtn[i],4)
            vLayout.addWidget(self.filesNames[i],1)
            self.ui.filesGrid.addLayout(vLayout, self.row, self.col)
            self.filesBtn[i].clicked.connect(lambda state, btn = i: self.openNotebook(self.f[btn])) 

            self.col += 1
            if (self.col % 3 == 0):
                self.row += 1
                self.col = 0
    
    def openNotebook(self, fileName):
        print(fileName)
        self.close()
        self.te = textEditor(fileName,self.client)


    def createFile(self):
        self.client.close()
        self.close()
        self.cf = createNewFile()


class textEditor(QtWidgets.QMainWindow):
    closed = QtCore.pyqtSignal()
    
    def __init__(self, fileName,client_obj):
        super(textEditor, self).__init__()
        self.create_new = False
        self.fileName = fileName
        #load ui file
        self.ui = Ui_secondWindow()
        self.ui.setupUi(self)
        
        self.client = client_obj
        #load text file
        self.loadTextFile()

        #Setting menubar actions
        self.ui.actionNew_file.triggered.connect(self.createFile)
        self.ui.actionSave_file.triggered.connect(self.close)
        
        #flag to set text to bold
        self.setBold = True

        self.fontSizeBox = QtWidgets.QSpinBox()
        
        font = QtGui.QFont('Times', 24)
        self.ui.textEdit.setFont(font)
        self.setCentralWidget(self.ui.textEdit)
        self.setWindowTitle('Text Editor')
        self.create_tool_bar()
        self.ui.textEdit.setFontPointSize(24)
        self.setWindowTitle(self.fileName)
        
        self.show()
        while self.isVisible():
            pos = self.ui.textEdit.textCursor().position()
            new_content = self.client.send(self.ui.textEdit.toHtml())
            self.ui.textEdit.clear()
            self.ui.textEdit.insertHtml(new_content)
            cursor = self.ui.textEdit.textCursor()
            cursor.setPosition(pos)
            
            self.ui.textEdit.setTextCursor(cursor)
            self.setFontSize()


            self.custom_Delay(500)


    def custom_Delay(self, t):
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(t, loop.quit)
        loop.exec_()

    def create_tool_bar(self):
        toolbar = QtWidgets.QToolBar()
 
        undoBtn = QtWidgets.QAction(QtGui.QIcon('./img/undo.png'), 'undo', self)
        undoBtn.triggered.connect(self.ui.textEdit.undo)
        toolbar.addAction(undoBtn)
        
        redoBtn = QtWidgets.QAction(QtGui.QIcon('./img/redo.png'), 'redo', self)
        redoBtn.triggered.connect(self.ui.textEdit.redo)
        toolbar.addAction(redoBtn)
        
        
        self.fontBox = QtWidgets.QComboBox(self)
        self.fontBox.addItems(["Courier Std", "Hellentic Typewriter Regular", "Helvetica", "Arial", "SansSerif", "Helvetica", "Times", "Monospace"])
        self.fontBox.activated.connect(self.setFont)
        toolbar.addWidget(self.fontBox)
        
        self.fontSizeBox.setValue(24)
        self.fontSizeBox.valueChanged.connect(self.setFontSize)
        toolbar.addWidget(self.fontSizeBox)
        
        rightAllign = QtWidgets.QAction(QtGui.QIcon('./img/right-align.png'), 'Right Allign', self)
        rightAllign.triggered.connect(lambda : self.ui.textEdit.setAlignment(QtCore.Qt.AlignRight))
        toolbar.addAction(rightAllign)
        
        leftAllign = QtWidgets.QAction(QtGui.QIcon('./img/left-align.png'), 'left Allign', self)
        leftAllign.triggered.connect(lambda : self.ui.textEdit.setAlignment(QtCore.Qt.AlignLeft))
        toolbar.addAction(leftAllign)
        
        centerAllign = QtWidgets.QAction(QtGui.QIcon('./img/center-align.png'), 'Center Allign', self)
        centerAllign.triggered.connect(lambda : self.ui.textEdit.setAlignment(QtCore.Qt.AlignCenter))
        toolbar.addAction(centerAllign)
        
        toolbar.addSeparator()
        
        boldBtn = QtWidgets.QAction(QtGui.QIcon('./img/bold.png'), 'Bold', self)
        boldBtn.triggered.connect(self.boldText)
        toolbar.addAction(boldBtn)
        
        underlineBtn = QtWidgets.QAction(QtGui.QIcon('./img/underline.png'), 'underline', self)
        underlineBtn.triggered.connect(self.underlineText)
        toolbar.addAction(underlineBtn)
        
        italicBtn = QtWidgets.QAction(QtGui.QIcon('./img/italic.png'), 'italic', self)
        italicBtn.triggered.connect(self.italicText)
        toolbar.addAction(italicBtn)
        
        
        self.addToolBar(toolbar)    
        
    def setFontSize(self):
        value = self.fontSizeBox.value()
        self.ui.textEdit.setFontPointSize(value)
        
    def setFont(self):
        font = self.fontBox.currentText()
        self.ui.textEdit.setFont(QtGui.QFont(font))
        
    def italicText(self):
        state = self.ui.textEdit.fontItalic()
        self.ui.textEdit.setFontItalic(not(state)) 
    
    def underlineText(self):
        state = self.ui.textEdit.fontUnderline()
        self.ui.textEdit.setFontUnderline(not(state))   
        
    def boldText(self):
       
        if self.setBold:
            self.ui.textEdit.setFontWeight(QtGui.QFont.Bold)
            
            print("bold", self.setBold)
        else:
            self.ui.textEdit.setFontWeight(QtGui.QFont.Normal)  
            print("notbold", self.setBold)
        self.setBold = not(self.setBold)

        

    
    def loadTextFile(self):
        ############################################################################################################################
        ######################## C.CONNECT #########################################################################################
        #read file contents
        result,content = self.client.connect(self.fileName)
        self.ui.textEdit.append(content)

        #################################################################################################################################
    def createFile(self):
        self.create_new = True
        self.close()
        self.cf = createNewFile()
     
    def closeEvent(self, event):
        ##############################################################################################################################
        ################################ C.SEND ######################################################################################
        #### save ####
        self.client.send(self.ui.textEdit.toHtml())
        self.client.close()

        ##############################################################################################################################
         # let the window close
        if not self.create_new:
            self.loadMainWindow()
        print("Closing edit")
        event.accept()

    def loadMainWindow(self):
        self.mw = mainWindow()


class createNewFile(QtWidgets.QMainWindow):
    def __init__(self):
        super(createNewFile, self).__init__()

        #load ui file
        self.ui = Ui_createTextFile()
        self.ui.setupUi(self)

        self.ui.createFileBtn.clicked.connect(self.createNewFile)     
        self.show()

    def createNewFile(self):
        global available_files
        # get file name
        self.newFileName = self.ui.newTextFileName.toPlainText()
        
        #hide text entery and the button
        self.ui.newTextFileName.setHidden(True)
        self.ui.createFileBtn.setHidden(True)
        self.ui.label.resize(200, 100);
        self.ui.label.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.ui.label.setAlignment(QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.ui.label)
        
        self.ui.label.setWordWrap(True);
        # check if file name already exit in the directory
        # f = [_ for _ in os.listdir('./textFiles') if _.endswith('txt')]

        print(self.newFileName)
        if self.newFileName in available_files:
            
            self.ui.label.setText("ERROR: text file already exists\nin the directory!")
            print("ERROR: text file already exists in the directory!")

        else:
            available_files.append(self.newFileName)
            self.ui.label.setText("File created, you can close this window now.")
        
        
    
    def custom_Delay(self,t):
        loop = QtCore.QEventLoop()
        QtCore.QTimer.singleShot(t, loop.quit)
        loop.exec_()

    def loadMainWindow(self):
        self.mw = mainWindow()
    def closeEvent(self, event):
        self.loadMainWindow()
        event.accept() # let the window close


app = QtWidgets.QApplication(sys.argv)
distTextEditor = mainWindow()
app.exec_()
