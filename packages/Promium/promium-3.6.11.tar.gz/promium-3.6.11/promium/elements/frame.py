
from promium.base import Element


class Frame(Element):

    def switch_to_frame(self):
        """Switch the focus from the main page content to the specific iframe"""
        self.driver.switch_to.frame(self.lookup())

    def exit_from_frame(self):
        """Switch the focus from the specific iframe to the main page content"""
        self.driver.switch_to.window(self.driver.current_window_handle)
