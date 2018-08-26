import PySide2.QtWidgets

from logic.TradeGlobals import GloVar
from gui.GlobalVariables import myLineEdit


class WidgetGlobalInput(PySide2.QtWidgets.QWidget):

    def __init__(self, parent, name):
        PySide2.QtWidgets.QWidget.__init__(self, parent)
        
        self.labelText = PySide2.QtWidgets.QLabel(self)
        self.labelText.setText(name)
        self.labelInput = myLineEdit(self, name)
        
        hbox = PySide2.QtWidgets.QHBoxLayout()
        hbox.addWidget(self.labelText, 1)
        hbox.addWidget(self.labelInput, 2)
        
        self.setLayout(hbox)
        self.labelInput.valueChanged.connect(self.setGlobalVariable)
        GloVar.signal_set.connect(self.getGlobalVariable)
 
    def setGlobalVariable(self, name, value):
        GloVar.set(name, value)
        
    def getGlobalVariable(self, name, variable):     
        if name ==  self.labelInput.name:
            self.labelInput.valueChanged.disconnect(self.setGlobalVariable)
            self.labelInput.setText(str(variable.value)) 
            self.labelInput.valueChanged.connect(self.setGlobalVariable)
                   
        
class TraidingInterface(PySide2.QtWidgets.QWidget):
    
    def __init__(self, parent):
        PySide2.QtWidgets.QWidget.__init__(self, parent)
        hbox = PySide2.QtWidgets.QHBoxLayout()
        
        self.button_start = PySide2.QtWidgets.QPushButton(self)
        self.button_start.setText("Start")
        self.button_stop = PySide2.QtWidgets.QPushButton(self)
        self.button_stop.setText("Stop")
        self.button_data_reset = PySide2.QtWidgets.QPushButton(self)
        self.button_data_reset.setText("Reset Data")
        
      
        hbox.addWidget(self.button_start)
        hbox.addWidget(self.button_stop)
        hbox.addWidget(self.button_data_reset)
        
        vbox = PySide2.QtWidgets.QVBoxLayout()
        vbox.addLayout(hbox)
    
        
        self.label_trade_source_name = WidgetGlobalInput(self, 'trade_source_name')
        self.label_trade_source_count = WidgetGlobalInput(self, 'trade_source_count')

        self.label_trade_target_name = WidgetGlobalInput(self, 'trade_target_name')
        self.label_trade_target_count = WidgetGlobalInput(self, 'trade_target_count')
                
        vbox.addWidget(self.label_trade_source_name)
        vbox.addWidget(self.label_trade_source_count)
        vbox.addWidget(self.label_trade_target_name)
        vbox.addWidget(self.label_trade_target_count)
        
        self.setLayout(vbox)
    
    
        
        
if __name__ == "__main__":
    app = PySide2.QtWidgets.QApplication([])
    MainWidget = TraidingInterface(parent=None)
    MainWidget.resize(800, 800)
    MainWidget.show()
    app.exec_()