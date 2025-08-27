from .imports import *

from .tabs import (
    runnerTab, functionsTab, collectFilesTab, diffParserTab,
    directoryMapTab, extractImportsTab, finderTab
)
from .imports.shared_state import SharedStateBus
from .imports.sharedBus import init_results_ui

def get_tabs_js(content=True,directory=True,collect=True,extract=True,diff=True):
    return {"content":{"text":"Find Content","tab":finderTab,"content":content,"bus":True},
        "directory":{"text":"Directory Map","tab":directoryMapTab,"bool":directory,"bus":True},
        "collect":{"text":"Collect Files","tab":collectFilesTab,"bool":collect,"bus":True},
        "extract":{"text":"Extract Python Imports","tab":extractImportsTab,"bool":extract,"bus":True},
        "diff":{"text":,"tab":diffParserTab,"bool":diff,"bus":True}
        }
def initiate_tabs(
    inner,bus=bus,
    parent=parent,
    content=True,
    directory=True,
    collect=True,
    extract=True,
    diff=True
    ):
    tabs_js = get_tabs_js(
        content=content,
        directory=directory,
        collect=collect,
        extract=extract,
        diff=diff
        )
    for key,value in tabs_js.items():
        vBool = value.get("bool") 
        if vBool not in [None,False]:
            vBus = value.get("bus")
            vTab = value.get("tab")
            if vBus not in [None,False]:
                vTAB = vTab(bus)
            else:
                vTAB = vTab()
            vTAB = set_self_log(vTAB)
            vTAB = init_results_ui(vTAB)
            inner.addTab(vTAB)
class ConsoleBase(QWidget):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(parent)
        self.bus = bus or SharedStateBus(self)
        self.setLayout(QVBoxLayout())
def set_self_log(self):
    self.log = QTextEdit()
    self.log.setReadOnly(True)
    self.log.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    return self
# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
class ConsoleBase(QWidget):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(parent)
        self.bus = bus or SharedStateBus(self)
        self.setLayout(QVBoxLayout())
# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
class finderConsole(ConsoleBase):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(bus=bus, parent=parent)
        inner = QTabWidget()
        self.layout().addWidget(inner)

        # all content tabs share THIS console’s bus
        inner.addTab(finderTab(self.bus),         "Find Content")
        inner.addTab(directoryMapTab(self.bus),   "Directory Map")
        inner.addTab(collectFilesTab(self.bus),   "Collect Files")
        inner.addTab(extractImportsTab(self.bus), "Extract Python Imports")
        inner.addTab(diffParserTab(self.bus),             "Diff (Repo)")

# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
class reactRunnerConsole(ConsoleBase):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(bus=bus, parent=parent)
        inner = QTabWidget()
        self.layout().addWidget(inner)

        # all content tabs share THIS console’s bus
        inner.addTab(runnerTab(),         "react Runner")
        inner.addTab(functionsTab(),   "Functions")


class MainShell(QMainWindow):
   def __init__(self, *, bus=None, parent=None):
        super().__init__(bus=bus, parent=parent,content=True,directory=True,collect=True,extract=True,diff=True)
        inner = QTabWidget()
        self.layout().addWidget(inner)
        tabs_js = {"content":{"text":"Find Content","tab":finderTab,"content":content,"bus":True},
             "directory":{"text":"Directory Map","tab":directoryMapTab,"bool":directory,"bus":True},
             "collect":{"text":"Collect Files","tab":collectFilesTab,"bool":collect,"bus":True},
             "extract":{"text":"Extract Python Imports","tab":extractImportsTab,"bool":diff,"bus":True},
             "diff":{"text":,"tab":diffParserTab,"bool":diff,"bus":True}
             }
        
        for key,value in tabs_js.items():
            vBool = value.get("bool") 
            if vBool not in [None,False]:
                vBus = value.get("bus")
                vTab = value.get("tab")
                
                
                
                if vBus not in [None,False]:
                    vTAB = vTab(self.bus)
                else:
                    vTAB = vTab()
                vTAB = set_self_log(vTAB)
                 = init_results_ui(vTAB)
                inner.addTab(vTAB)
                
