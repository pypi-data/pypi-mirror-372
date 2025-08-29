#   from orangecontrib.HLIT_dev.utils.hlit_crawler import hlit_crawler
#   out_data = hlit_crawler(in_data)

import os
import sys
import Orange.data
from AnyQt.QtWidgets import QApplication
from Orange.widgets import widget
from Orange.widgets.utils.signals import Input, Output
from Orange.widgets.settings import Setting



if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management
    from Orange.widgets.orangecontrib.HLIT_dev.utils.hlit_python_api import daemonizer_no_input_output
else:
    from orangecontrib.AAIT.utils import thread_management
    from orangecontrib.HLIT_dev.utils.hlit_python_api import daemonizer_no_input_output


def _run_daemonizer(indata,
                    ip_port="127.0.0.1:8000",
                    workflow_key="titiatoto",
                    poll_sleep=0.3):
    """Worker function executed inside the Thread."""
    rc = daemonizer_no_input_output(
        ip_port, workflow_key, temporisation=poll_sleep
    )
    if rc != 0:
        raise RuntimeError(f"daemonizer finished with code {rc}")
    return indata



class OWAgentIA(widget.OWWidget):
    name = "AgentIA"
    description = "Runs daemonizer_no_input_output in a thread; passes data through."
    icon = "icons/agent.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/agent.png"
    priority = 1091
    want_main_area = False
    # want_control_area = False

    ip_port = Setting("127.0.0.1:8000")
    workflow_key = Setting("titiatoto")
    poll_sleep = Setting(0.3)


    class Inputs:
        data = Input("Data", Orange.data.Table)

    class Outputs:
        data = Output("Data", Orange.data.Table)


    def __init__(self):
        super().__init__()
        # self._token = None         # keeps last incoming token
        self.data = None
        self.thread = None
        self.autorun = True
        self.result = None

        # hard-coded server params
        self.ip_port = "127.0.0.1:8000"
        self.workflow_key = "titiatoto"
        self.poll_sleep = 0.3

        self.post_initialized()

        #form = QFormLayout()
        #self.le_ip = QLineEdit(self.ip_port)
        #self.le_key = QLineEdit(self.workflow_key)
        #self.le_sleep = QLineEdit(str(self.poll_sleep))
        #form.addRow("Server", self.le_ip)
        #form.addRow("Workflow key", self.le_key)
        #form.addRow("Sleep (s)", self.le_sleep)
        #gui.widgetBox(self.controlArea, orientation=form)
        #self.setWindowTitle(f"{self.name}: idle")

    @Inputs.data
    def set_data(self, in_data):
        self.data = in_data
        if self.autorun:
            self.run()

    def run(self):
        # if thread is running quit
        if self.thread is not None:
            self.thread.safe_quit()

        if self.data is None:
            return
        # Verificiation of in_data needed ?

        self.progressBarInit()

        self.thread = thread_management.Thread(_run_daemonizer,self.data, self.ip_port, self.workflow_key, self.poll_sleep)
        self.thread.progress.connect(self.handle_progress)
        self.thread.result.connect(self.handle_result)
        self.thread.finish.connect(self.handle_finish)
        self.thread.start()

    def handle_progress(self, value: float) -> None:
        self.progressBarSet(value)

    def handle_result(self, result):
        try:
            self.result = result
            self.Outputs.data.send(result)
        except Exception as e:
            print("An error occurred when sending out_data:", e)
            self.Outputs.data.send(None)
            return

    def handle_finish(self):
        print("Crawler finished")
        self.progressBarFinished()

    def post_initialized(self):
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWAgentIA()
    w.show()
    if hasattr(app, "exec"):
        app.exec()
    else:
        app.exec_()



