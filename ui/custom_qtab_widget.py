from PyQt5.QtWidgets import QTabWidget


class CustomQTabWidget(QTabWidget):

    def __init__(self):
        super().__init__()

    def dropEvent(self, e):
        # 右键拖拽
        print(self.parent.TABINDEX)
