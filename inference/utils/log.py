import logging

# https://stackoverflow.com/questions/37703609/using-python-logging-with-aws-lambda
if logging.getLogger().hasHandlers():
    ### Local log
    # The Lambda environment pre-configures a handler logging to stderr.
    # If a handler is already configured,
    # `.basicConfig` does not execute. Thus we set the level directly.
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

else:
    ### Lambda log
    import logging as logger

    logger.basicConfig(
        format="%(asctime)s - [%(levelname)s] %(message)s", level=logger.INFO
    )
