from multiprocessing import Process, Manager, active_children
import multiprocessing.managers as mpmanagers
from queue import Full, Empty
import logging


_logger = logging.getLogger(__name__)

# multiprocessing has a bug in some versions of python where the AutoProxy
# method is called with an extra parameter (manager_owned), we are wrapping
# that method so we can receive (and ignore) that extra parameter without
# raising an exception. More info in `https://bugs.python.org/issue30256`
ORIGINAL_AUTOPROXY = mpmanagers.AutoProxy


def fixed_autoproxy(token, serializer, manager=None, authkey=None,
                    exposed=None, incref=True, manager_owned=False):
    return ORIGINAL_AUTOPROXY(token, serializer, manager, authkey,
                              exposed, incref)


mpmanagers.AutoProxy = fixed_autoproxy


class WorkerManager:

    def __init__(self, worker_type, workers):
        # If the workers will only be used to report the status to orchest,
        # just start one worker.
        self._workers = workers if worker_type != 'Status worker' else 1
        self.available_workers = Manager().Queue(workers)
        _logger.info('Initializing the workers for the %s', worker_type)
        self.start_workers()

    def start_workers(self):
        """ Starts WorkerUnit instances ready to attend the messages equal
        to the amount of desired workers.
        """
        for _ in range(self._workers):
            self.add_worker()

    def add_worker(self):
        """ Adds a new worker to the queue of workers, used to create the
        initial "pool"" of workers, and to replace the workers that are removed
        when a new message arrives.
        """
        try:
            self.available_workers.put(WorkerUnit, block=False)
        except Full:
            _logger.info("Can't add more workers, limit reached: %s",
                         self._workers)
        _logger.info('New worker started')

    def start_job(self, func, data):
        """ Takes a new worker from the "pool" of workers and
        starts a new process in  the background where the worker attends a job.

        :param func: function to be executed by the worker.
        :param data: Dictionary with the data of the message received to be passed to
            the function.

        :return: True it the job started successfully, False otherwise.
        """
        # Remove the defunct processes of the workers that already finished
        # before starting a new process
        active_children()
        try:
            worker = self.available_workers.get(block=False)
            worker_inst = worker(manager=self)
        except Empty:
            _logger.debug('No available workers for this job')
            return False
        _logger.info('Working on the message:\n%s', data)
        worker_process = Process(target=worker_inst.work, args=(func, data,))
        worker_process.start()
        return True


class WorkerUnit:

    def __init__(self, manager):
        self._manager = manager

    def work(self, func, data):
        """ Executes the provided function with the provided data and adds
        a new worker to the pool after it finishes.
        """
        func(data)
        self._manager.add_worker()
        _logger.info('Job done')
