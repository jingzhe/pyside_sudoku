# Copyright (c) 2010-2011 Jingzhe Yu. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public Licence as published
# by the Free Software Foundation, either version 2 of the Licence, or
# version 3 of the Licence, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public Licence for more details.

import sys
import os
import platform

import PyQt4
from PyQt4 import QtCore 
from PyQt4 import QtGui 

import qrc_sudoku

__version__ = '1.0'

class Calculate:

    def __init__(self):
        self.str1 = '0' * 81
        self.str2 = '0' * 81
        self.answer = 0
        self.done = False
        self.loop = 0

    def same_row(self, i, j): 
        return (i/9 == j/9)
    
    def same_col(self, i, j): 
        return (i-j) % 9 == 0
    
    def same_block(self, i, j): 
        return (i/27 == j/27 and i%9/3 == j%9/3)

    def print_format(self, a):
        for i in range(9):
            for j in range(9):
                print '%s ' % a[9*i + j],
            print ''    

    def r(self, a):
        self.loop += 1
        if self.answer == 1 and self.loop > 120000:
            self.done = True

        i = a.find('0')
        if i == -1:
            self.print_format(a)
            print ''
            self.answer += 1
            if self.answer == 1:
                self.str1 = a
                print 'loop %d' % self.loop

            elif self.answer == 2:
                self.str2 = a
                self.done = True
            return

        excluded_numbers = set()
        for j in range(81):
            if self.same_row(i,j) or self.same_col(i,j) or self.same_block(i,j):
                if a[j] != '0':
                    excluded_numbers.add(a[j])
        for m in '123456789':
            if m not in excluded_numbers:
                if self.done:
                    return
               # At this point, m is not excluded by any row, column, or block, so let's place it and recurse
                self.r(a[:i]+m+a[i+1:])

class RenderArea(QtGui.QWidget):

    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.pen = QtGui.QPen()
        self.brush = QtGui.QBrush()
        self.antialiased = False
        self.transformed = False
        self.setBackgroundRole(QtGui.QPalette.Base)
        self.mousePressed = False
        self.mouseX = 0
        self.mouseY = 0
        self.lineEdit = QtGui.QLineEdit(self)
        self.lineEdit.setFixedSize(QtCore.QSize(50,50))
        self.lineEdit.setInputMask('D')
        self.lineEdit.setAlignment(QtCore.Qt.AlignHCenter)
        self.lineEdit.hide()
        self.str = '0' * 81
        self.oldIndex = -1
        self.start = False
        self.origStr = '0' * 81

    def minimumSizeHint(self):
        return QtCore.QSize(100, 100)

    def sizeHint(self):
        return QtCore.QSize(400, 200)

    def setShape(self, shape):
        self.shape = shape
        self.update()

    def setPen(self, pen):
        self.pen = pen
        self.update()

    def setBrush(self, brush):
        self.brush = brush
        self.update()

    def setAntialiased(self, antialiased):
        self.antialiased = antialiased
        self.update()

    def setTransformed(self, transformed):
        self.transformed = transformed
        self.update()
    def mousePressEvent(self, event):
        if self.oldIndex != -1 and self.lineEdit.text() != '':
            self.str = self.str[:self.oldIndex] + self.lineEdit.text() + self.str[self.oldIndex+1:]
        if self.oldIndex != -1 and self.lineEdit.text() == '':
            self.str = self.str[:self.oldIndex] + '0' + self.str[self.oldIndex+1:]

        self.mouseX = event.x()
        self.mouseY = event.y()
        if self.mouseX > 50 and self.mouseX < 500 and self.mouseY > 50 and self.mouseY < 500:
            self.lineEdit.show()
            self.mousePressed = True
            self.lineEdit.move(QtCore.QPoint(self.mouseX/50*50, self.mouseY/50*50))
            self.oldIndex = (self.mouseY/50-1) * 9 + self.mouseX/50-1
            self.lineEdit.setText(self.str[self.oldIndex])
            self.lineEdit.cursorBackward(True, 1)
            self.lineEdit.setFocus()
        else:
            self.lineEdit.hide()
        self.update()

    def updateLast(self):
        if self.oldIndex != -1 and self.lineEdit.text() != '':
            self.str = self.str[:self.oldIndex] + self.lineEdit.text() + self.str[self.oldIndex+1:]
        if self.oldIndex != -1 and self.lineEdit.text() == '':
            self.str = self.str[:self.oldIndex] + '0' + self.str[self.oldIndex+1:]

        self.lineEdit.hide()
        self.update()

    def paintEvent(self, event):
        rect = QtCore.QRect(10, 20, 80, 60)

        painter = QtGui.QPainter()
        painter.begin(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        if self.antialiased:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.save()
        pen = QtGui.QPen()
        pen.setBrush(QtCore.Qt.red)
        for i in range(10):
            if i % 3 == 0:
                pen.setWidth(3)
            else:
                pen.setWidth(1)
            painter.setPen(pen)
            painter.drawLine(QtCore.QPoint(50, 50+50*i), QtCore.QPoint(500, 50+50*i))
            painter.drawLine(QtCore.QPoint(50+50*i, 50), QtCore.QPoint(50+50*i, 500))

        for i in range(81):
            textX = ((i%9)+1)*50 + 25
            textY = ((i/9)+1)*50 + 25
            if self.origStr[i] != '0':
                penOrig = QtGui.QPen()
                penOrig.setBrush(QtCore.Qt.blue)
                penOrig.setWidth(2)
                painter.setPen(penOrig)
                painter.drawText(textX, textY, self.str[i])
            else:
                if self.str[i] != '0':
                    painter.setPen(pen)
                    painter.drawText(textX, textY, self.str[i])

        if self.mousePressed:
            rect = QtCore.QRect(self.mouseX/50*50, self.mouseY/50*50, 50, 50)
            painter.setBrush(QtCore.Qt.yellow)
            painter.drawRect(rect)
            self.mousePressed = False

        painter.restore()

        painter.end()

class Sudoku(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Sudoku, self).__init__(parent)        
        self.resize(600, 600)
        self.filename  = None
        self.filetuple = None
        self.dirty = False  # Refers to Data Page only.
        self.renderArea  = RenderArea(self)
        self.setCentralWidget(self.renderArea)
        self.renderArea.setFocus()
        menubar = QtGui.QMenuBar(self)
#        menubar.setGeometry(QtCore.QRect(0, 0, 100, 9))
        menu_File = QtGui.QMenu(menubar)
        self.menu_Solve = QtGui.QMenu(menubar)
        self.menu_Help = QtGui.QMenu(menubar)
        self.setMenuBar(menubar)
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.action_New = QtGui.QAction(self)
        self.actionSave_As = QtGui.QAction(self)
        self.action_Save = QtGui.QAction(self)
        self.action_Open = QtGui.QAction(self)
        self.action_Quit = QtGui.QAction(self)
        self.action_About = QtGui.QAction(self)
        self.actionShow_GPL = QtGui.QAction(self)
        self.action_Clear = QtGui.QAction(self)
        self.action_Start = QtGui.QAction(self)
        self.action_Solve = QtGui.QAction(self)
        self.action_Next = QtGui.QAction(self)
        self.action_GPL = QtGui.QAction(self)
        self.action_Help = QtGui.QAction(self)
        menu_File.addAction(self.action_New)
        menu_File.addAction(self.action_Open)
        menu_File.addAction(self.actionSave_As)
        menu_File.addAction(self.action_Save)
        menu_File.addSeparator()
        menu_File.addAction(self.action_Quit)
        self.menu_Solve.addAction(self.action_Clear)
        self.menu_Solve.addAction(self.action_Start)
        self.menu_Solve.addAction(self.action_Solve)
        self.menu_Solve.addAction(self.action_Next)
        self.menu_Help.addAction(self.action_About)
        self.menu_Help.addAction(self.action_GPL)
        self.menu_Help.addAction(self.action_Help)
        menubar.addAction(menu_File.menuAction())
        menubar.addAction(self.menu_Solve.menuAction())
        menubar.addAction(self.menu_Help.menuAction())        
        self.setWindowTitle("Main Window")
        menu_File.setTitle("&File")        
        self.menu_Solve.setTitle("&Solve")
        self.menu_Help.setTitle("&Help")
        self.action_New.setText("&New") 
        self.action_Open.setText("&Open")       
        self.actionSave_As.setText("Save &As")
        self.action_Save.setText("&Save")
        self.action_Quit.setText("&Quit")
        self.action_Clear.setText("&Clear")
        self.action_Start.setText("&Start")
        self.action_Solve.setText("&Solve")
        self.action_Next.setText("&Next")

        self.action_About.setText("&About")
        self.action_GPL.setText("&GPL")
        self.action_Help.setText("&Help")
        self.action_Quit.triggered.connect(self.close)
        allToolBar = self.addToolBar("AllToolBar") 
        allToolBar.setObjectName("AllToolBar") 
        self.addActions(allToolBar, (self.action_Open, self.actionSave_As,\
                        self.action_Save, self.action_Solve,\
                        self.action_Quit ))
        self.action_New.triggered.connect(self.fileNew)
        self.action_Open.triggered.connect(self.fileOpen)
        self.actionSave_As.triggered.connect(self.fileSaveAs)
        self.action_Save.triggered.connect(self.fileSave)
        self.action_Clear.triggered.connect(self.sudokuClear)
        self.action_Start.triggered.connect(self.sudokuStart)
        self.action_Solve.triggered.connect(self.sudokuSolve)
        self.action_Next.triggered.connect(self.sudokuNext)

        self.action_About.triggered.connect(self.aboutBox)
        self.action_GPL.triggered.connect(self.displayGPL)
        self.action_Help.triggered.connect(self.help)
        self.action_New = self.editAction(self.action_New, None,\
                            'ctrl+N', 'filenew', 'New File.')   
        self.action_Open = self.editAction(self.action_Open, None, 
                            'ctrl+O', 'fileopen', 'Open File.')
        self.actionSave_As = self.editAction(self.actionSave_As,\
                            None, 'ctrl+A', 'filesaveas',\
                            'Save and Name File.')
        self.action_Save = self.editAction(self.action_Save, None, 
                            'ctrl+S', 'filesave', 'Save File.')
        self.action_Solve = self.editAction(self.action_Solve, None, 
                            'ctrl+L', 'solve', 'Solve Structure.')                                   
        self.action_About = self.editAction(self.action_About, None, 
                            'ctrl+B', 'about','Pop About Box.')                                  
        self.action_GPL = self.editAction(self.action_GPL, None, 
                            'ctrl+G', 'licence', 'Show Licence') 
        self.action_Help = self.editAction(self.action_Help, None, 
                            'ctrl+H', 'help', 'Show Help Page.')
        self.action_Quit =  self.editAction(self.action_Quit, None, 
                            'ctrl+Q', 'quit', 'Quit the program.')
        self.cal = Calculate()
        self.answer = 0
    
    def setDirty(self):
        self.dirty = True
    
    def clearDirty(self):
        'Clear dirty flag'
        self.dirty = False
    
    def fileNew(self):
        self.clearDirty()
        print "file new"

    def okToContinue(self):
        if self.dirty:
            reply = QMessageBox.question(self,
                    "Data Loader - Unsaved Changes",
                    "Save unsaved changes?",
                    QMessageBox.Yes|QMessageBox.No|QMessageBox.Cancel)
            if reply == QMessageBox.Cancel:
                return False
            elif reply == QMessageBox.Yes:
                self.clearDirty()
                return self.fileSave()
        return True
    
    def okRead(self):
        'Pop-up a warning message.'
        reply = QMessageBox.warning(self,
                "Warning",
                '''\nFile Open and Save is possible only in Data Page!
\n\(Use SaveAs for Solution Page)''', QMessageBox.Ok)
        return True

    def fileOpen(self):
        print "file open"
                
    def loadFile(self, fname=None):
        print "load file"
    
    def fileSave(self):
        print "file save"

    def fileSaveAs(self):
        print "file save as"


    def sudokuClear(self):
        self.cal.str1 = '0' * 81
        self.cal.str2 = '0' * 81
        self.cal.answer = 0
        self.cal.done = False
        self.loop = 0
        self.renderArea.str = '0' * 81
        self.renderArea.oldIndex = -1
        self.renderArea.start = False
        self.renderArea.origStr = '0' * 81
        self.renderArea.update()

    def sudokuStart(self):
        self.renderArea.start = True
        self.renderArea.origStr = self.renderArea.str
        self.renderArea.update()

    def sudokuSolve(self):
        print "sudok solve"
        self.renderArea.updateLast()
        init_code = str(self.renderArea.str)
        self.cal.r(init_code)
        self.renderArea.str = self.cal.str1
            
        self.renderArea.update()

    def sudokuNext(self):
        if self.cal.answer == 2:
            if self.answer == 0:
                self.renderArea.str = self.cal.str2
                self.answer = 1
            else:
                self.renderArea.str = self.cal.str1
                self.answer = 0
        else:
            self.renderArea.str = self.cal.str1
            
        self.renderArea.update()


    def aboutBox(self):
        '''Popup a box with about message.'''
        QtGui.QMessageBox.about(self, "Sudoku solver",
                """<b>Solve any Sudoku problem.</b> v %s
                <p>Copyright &copy; 2011 Jingzhe Yu. 
                All rights reserved in accordance with
                GPL v2 or later - NO WARRANTIES!
                <p>This progam can solve any Sudoku in very short time. 
                <p>Python %s -  PySide version %s - Qt version %s on\
                %s""" % (__version__, platform.python_version(),\
                PySide.__version__,  PySide.QtCore.__version__,
                platform.system()))
              
    def displayGPL(self):
        '''Read and display GPL licence.'''
        QtGui.QMessageBox.about(self, "GPL", open('COPYING.txt').read())
        self.dirty = False
        self.filename = 'COPYING.txt'
        self.updateStatus('GPL displayed.')

    def help(self):
        '''Read and display a help file- currently the README.txt.'''
        QtGui.QMessageBox.about(self, "help", open('README.txt').read())
        self.dirty = False
        self.filename = 'README.txt'
        self.updateStatus('README displayed.')
        
    def addActions(self, target, actions):
        '''Actions are added to Tool Bar.'''
        for action in actions:
            if action is None:
                target.addSeparator()
            else:
                target.addAction(action)
    
    def editAction(self, action, slot=None, shortcut=None, icon=None,
                     tip=None):
        '''This method adds to action: icon, shortcut, ToolTip,\
        StatusTip and can connect triggered action to slot '''
        if icon is not None:
            action.setIcon(QtGui.QIcon(":/%s.png" % (icon)))
        if shortcut is not None:
            action.setShortcut(shortcut)
        if tip is not None:
            action.setToolTip(tip)
            action.setStatusTip(tip)
        if slot is not None:
            action.triggered.connect(slot)                        
        return action



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    frame = Sudoku()
    frame.show()
    sys.exit(app.exec_())
    

