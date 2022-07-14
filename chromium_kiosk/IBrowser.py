from chromium_kiosk.config import Config


class IBrowser:

    def set_config(self, config: Config):
        raise NotImplementedError

    def run(self) -> None:
        """
        Start browser
        :return: 
        """
        raise NotImplementedError
