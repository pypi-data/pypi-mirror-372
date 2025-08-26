from .execution import Execution, ExecutionStepLog


class ILogger:
    """
    logger interface used within a pipeline and context.
    """

    def write_log(self, message: str, level: int = 7):
        """
        write a log
        :param str message: message to write.
        :param int level: from 1 critical to 7 verbose.
        """
        pass

    def notify_step(self, step_log: ExecutionStepLog):
        """
        notify the listeners and watchers on current step status.
        :param wizata_dsapi.ExecutionStepLog step_log: step log.
        """
        pass

    def notify_execution(self, execution: Execution):
        """
        notify the listeners and watchers on current execution status.
        :param wizata_dsapi.Execution execution: execution log.
        """
        pass
