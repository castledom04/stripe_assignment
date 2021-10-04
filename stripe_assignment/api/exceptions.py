class PaymentsAlreadySubscribedError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__()


class PaymentsCardError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__()


class PaymentsGatewayError(Exception):

    def __init__(self, message):
        self.message = message
        super().__init__()
