import logging

_setup = False
root_logger = None
kognic_logger = None

TEXT_FORMAT = "%(asctime)-15s %(levelname)-s [%(name)-25s] %(message)s"


def setup_logging(level: str):
    global _setup
    if _setup:
        raise RuntimeError("Logging is already setup")

    module_log_levels = dict()
    if level is not None:
        # force override
        module_log_levels["root"] = level
        module_log_levels["kognic"] = level

    global root_logger, kognic_logger
    root_logger = logging.getLogger()
    kognic_logger = root_logger.getChild("kognic")

    for lg, lvl in module_log_levels.items():
        logger = root_logger if lg == "root" else logging.getLogger(lg)
        logger.setLevel(logging.getLevelName(lvl))
    logging.basicConfig(format=TEXT_FORMAT)

    _setup = True
