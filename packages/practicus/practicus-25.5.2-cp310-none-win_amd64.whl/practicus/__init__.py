import sys

from .shared import AppDef
from .app_conf import app_conf_glbl
from .app import PRTApp
from .app_starter import AppStarter


def run(practicus_app: PRTApp | None = None):
    """
    Starts Practicus AI Studio Application.
    :return: None
    """
    run_(practicus_app)


def run_(practicus_app: PRTApp | None = None):
    """
    Starts Practicus AI Studio Application.
    :return: True if successful, otherwise False
    """
    if practicus_app is None:
        practicus_app = PRTApp(terminal_args=sys.argv)

    try:
        if PRTApp.is_packaged_app:
            pkg_or_lib = "packaged app"
        else:
            pkg_or_lib = "practicus library"

        _ = app_conf_glbl  # this needs to be imported to make sure logging config is also loaded
        AppStarter.logger.info(
            f"Starting Practicus AI Studio v{AppDef.APP_VERSION} "
            f"(Python v{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}, "
            f"running from {pkg_or_lib}) built on {AppDef.BUILD_DATE}"
        )

        AppStarter.create_folders_and_save_supporting_files()

        _app_starter = AppStarter(practicus_app)
        _app_starter.start()

        _app_starter.logger.debug("Running clean-up tasks to shutdown Practicus AI Studio..")
        # app_starter.main_window.destroy()  # this started causing issues after Qt6 + web page tab opened. removing
        _app_starter.main_window.run_shutdown_cleanup_tasks()  # type: ignore[union-attr]
        _app_starter.logger.info("Shutting down..\n\n")
        _app_starter.app.quit()
        sys.exit(0)
    except Exception as ex:
        try:
            import traceback

            trace = str(traceback.format_exc())
        except:
            trace = ""

        err_msg = (
            "An error occurred while starting Practicus AI Studio. "
            "Please consider the below if you the issue persists.\n"
            "1) Reinstall the application\n"
            "2) If you are using your own Python deployment, create a new virtual environment.\n"
            "3) Backup and then delete the hidden .practicus folder in your home directory.\n\n"
            "%s: %s" % (ex.__class__.__name__, ex)
        )

        try:
            print(err_msg, file=sys.stderr)
            if trace:
                print(trace, file=sys.stderr)
        except:
            print(err_msg)

        try:
            from PyQt6.QtWidgets import QMessageBox

            msg_box = QMessageBox()
            msg_box.setText(err_msg)
            msg_box.setIcon(QMessageBox.Icon.Critical)
            if trace:
                msg_box.setDetailedText(trace)
            msg_box.exec()
        except:
            try:
                from PyQt6.QtWidgets import QMessageBox

                msg_box = QMessageBox()
                msg_box.setText(err_msg)
                msg_box.setIcon(QMessageBox.Icon.Critical)
                if trace:
                    msg_box.setDetailedText(trace)
                msg_box.exec()
            except:
                pass

        try:
            from practicus.log_manager import get_logger, Log

            logger = get_logger(Log.APP)
            logger.error(err_msg, exc_info=True)
        except:
            pass

    finally:
        try:
            del _app_starter
        except:
            pass


try:
    from practicus.shared import AppDef

    __version__ = AppDef.APP_VERSION
except:
    __version__ = "0.0.0"


if __name__ == "__main__":
    run_()
