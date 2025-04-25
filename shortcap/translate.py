import logging
from typing import List
import argostranslate.package
import argostranslate.translate

logger = logging.getLogger("shortcap.emojis")


class TranslationError(Exception):
    """Custom exception class for handling errors during emojis operations"""

    pass


def check_package_installed(from_code: str, to_code: str) -> bool:
    try:
        installed_packages: List[argostranslate.package.Package] = (
            argostranslate.package.get_installed_packages()
        )
        for package in installed_packages:
            if package.from_code == from_code and package.to_code == to_code:
                return True
        return False
    except Exception as e:
        logger.error(f"Error checking installed package: {str(e)}")
        raise TranslationError(f"Error checking installed package: {str(e)}")


def install_package(from_code: str, to_code: str) -> None:
    try:
        argostranslate.package.update_package_index()
        available_packages: List[argostranslate.package.Package] = (
            argostranslate.package.get_available_packages()
        )
        package_to_install = next(
            filter(
                lambda x: x.from_code == from_code and x.to_code == to_code,
                available_packages,
            )
        )
        argostranslate.package.install_from_path(package_to_install.download())
    except Exception as e:
        logger.error(f"Error installing package: {str(e)}")
        raise TranslationError(f"Error installing package: {str(e)}")


def translate(text: str, from_code: str) -> str:
    to_code = "en"
    try:
        if from_code != "en":
            if not check_package_installed(from_code, to_code):
                install_package(from_code, to_code)
            translated_text = argostranslate.translate.translate(
                text, from_code, to_code
            )
            return translated_text
        return text
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        raise TranslationError(f"Error translating text: {str(e)}")
