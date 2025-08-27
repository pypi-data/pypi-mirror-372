import threading

class _GatewayEvent(object):

    __process_exit_handlers = []
    __thread_exit_handlers = {}

    @classmethod
    def registerGatewayProcessExitHandler(cls, func):
        """Register a function to be called when Gateway process exits.
        Gateway process exits when the Gateway is being shutdown.
        During a hard shutdown, the calls are made right before the process is forcefully killed.
        During a soft shutdown, the calls are made when the last user thread is finished.
        The function doesn't take any arguments."""
        cls.__process_exit_handlers.append(func)

    @classmethod
    def registerGatewayThreadExitHandler(cls, func):
        """Register a function to be called when the current Gateway thread exits.
        A thread can register multiple thread exit handlers.
        The function doesn't take any arguments."""
        thread_id = threading.get_ident()
        if cls.__thread_exit_handlers.get(thread_id) == None:
            cls.__thread_exit_handlers[thread_id] = []
        cls.__thread_exit_handlers[thread_id].append(func)


    @classmethod
    def _call_gateway_process_exit_handlers(cls):
        """Call all functions that were registered for process exit.
        Functions are called in the reverse order of registration, and exceptions are ignored."""
        for func in reversed(cls.__process_exit_handlers):
            try:
                func()
            except:
                pass

    @classmethod
    def _call_gateway_thread_exit_handlers(cls):
        """Call all functions that were registered as thread exit handlers for the current thread.
        Functions are called in the reverse order of registration, and exceptions are ignored."""
        thread_id = threading.get_ident()
        if cls.__thread_exit_handlers.get(thread_id) != None:
            for func in reversed(cls.__thread_exit_handlers[thread_id]):
                try:
                    func()
                except:
                    pass
            del cls.__thread_exit_handlers[thread_id]
    

