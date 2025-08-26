class WizardStep:
    """
    deprecated - define a UI required step on the wizard.
    """

    def __init__(self, step_id, order: int):
        self.step_id = step_id
        self.order = order


class WizardFunction:
    """
    deprecated - define a function to be used within the wizard.
    :ivar str title: display title representing the function.
    :ivar str function: technical name of the function.
    :ivar bool is_beta: set if the function is only active on beta environments.
    """

    def __init__(self, title, function, is_beta=False, restricted_domain=None):
        self.title = title
        self.function = function
        self.restricted_domain = restricted_domain
        self.is_beta = is_beta
        self.steps = []

    def append_step(self, step: WizardStep):
        """
        append a step to steps.
        :param wizata_dsapi.WizardStep step: step to append.
        """
        self.steps.append(step)
