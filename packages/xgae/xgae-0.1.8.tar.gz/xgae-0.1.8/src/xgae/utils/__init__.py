import logging

def handle_error(e: Exception) -> None:
    import traceback

    logging.error("An error occurred: %s", str(e))
    logging.error("Traceback details:\n%s", traceback.format_exc())
    raise (e) from e

