from .imports import *

from .tabs import (
    runnerTab, functionsTab, collectFilesTab, diffParserTab,
    directoryMapTab, extractImportsTab, finderTab
)
class ConsoleBase(QWidget):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(parent)
        self.bus = bus or SharedStateBus(self)
        self.setLayout(QVBoxLayout())
# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
class ContentFinderConsole(ConsoleBase):
    def __init__(self, *, bus=None, parent=None,content=True,directory=True,collect=True,extract=True,diff=True):
        super().__init__(bus=bus, parent=parent)
        inner = QTabWidget()
        self.layout().addWidget(inner)
        tabs_js = {"content":{"text":"Find Content","tab":finderTab,"content":content,"bus":True},
             "directory":{"text":"Directory Map","tab":directoryMapTab,"bool":directory,"bus":True},
             "collect":{"text":"Collect Files","tab":collectFilesTab,"bool":collect,"bus":True},
             "extract":{"text":"Extract Python Imports","tab":extractImportsTab,"bool":diff,"bus":True},
             "diff":{"text":"Diff Parser","tab":diffParserTab,"bool":diff,"bus":True}
             }
     
        for key,value in tabs_js.items():
            vBool = value.get("bool") 
            if vBool not in [None,False]:
                vBus = value.get("bus")
                vTab = value.get("tab")
                set_self_log(vTab)
                init_results_ui(vTab)
                
                
                if vBus not in [None,False]:
                    vTAB = vTab(self.bus)
                else:
                    vTAB = vTab()
                
                inner.addTab(vTAB)
                
# Content Finder = the nested group you built (Find Content, Directory Map, Collect, Imports, Diff)
class reactRunnerConsole(ConsoleBase):
    def __init__(self, *, bus=None, parent=None):
        super().__init__(bus=bus, parent=parent)
        inner = QTabWidget()
        self.layout().addWidget(inner)

        # all content tabs share THIS console’s bus
        inner.addTab(runnerTab(),         "react Runner")
        inner.addTab(functionsTab(),   "Functions")

class reactFinderShell(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Abstract Tools")
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # If you want these consoles independent, give each its OWN bus.
        # If you want them to share state globally, make ONE bus and pass it to all.
        self.reachRunner   = reactRunnerConsole()                # independent
        self.contentFinder = ContentFinderConsole()              # own bus for content-group only

        self.tabs.addTab(self.reachRunner,   "Reach Runner")
        self.tabs.addTab(self.contentFinder, "Content Finder")
