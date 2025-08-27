""" {project_name.replace('_', ' ')} title

doc string of main module implemented via the Kivy framework.

TODO: after the creation of this module from the templates: correct/replace "AppName" with the name/title of your app.
      also the 3 inline options ``pylint: disable`` should be removed from the kivy/ae.kivy import statements and
      the ``noqa: F541 # pylint: disable=W1309`` from the 2 app class methods on_clipboard_key_c/on_clipboard_key_v().
"""
from kivy.core.clipboard import Clipboard                # type: ignore # pylint: disable=import-error

from ae.kivy.apps import KivyMainApp                     # type: ignore # pylint: disable=import-error,no-name-in-module
from ae.kivy_sideloading import SideloadingMainAppMixin  # type: ignore # pylint: disable=import-error,no-name-in-module


__version__ = '{NULL_VERSION}'


class AppNameApp(SideloadingMainAppMixin, KivyMainApp):
    """ app class """
    def on_clipboard_key_c(self, lit: str = ""):
        """ copy focused item or the currently displayed node items to the OS clipboard.

        :param lit:             string literal to copy (def=current_item_or_node_literal()).
        """
        self.vpo(f"AppName.on_clipboard_key_c: copying {{lit}}")    # noqa: F541 # pylint: disable=W1309
        Clipboard.copy(lit)

    def on_clipboard_key_v(self):
        """ paste copied item or all items of the current node from the OS clipboard into the current node. """
        self.vpo(f"AppName.on_clipboard_key_v: pasting {{Clipboard.paste()}}")    # noqa: F541 # pylint: disable=W1309

    def on_clipboard_key_x(self):
        """ cut focused item or the currently displayed node items to the OS clipboard. """
        self.vpo("{project_name}.on_clipboard_key_x: cutting")
        # Clipboard.copy(lit) THEN cut

    def on_key_press(self, modifiers: str, key_code: str) -> bool:
        """ check key press event to be handled and processed as command/action.

        :param modifiers:       modifier keys.
        :param key_code:        code of the pressed key.
        :return:                True if key press event was handled, else False.
        """
        self.vpo(f"{project_name}.on_key_press {{modifiers}}+{{key_code}}")

        # noinspection PyUnresolvedReferences
        return super().on_key_press(modifiers, key_code)


# app start
if __name__ in ('__android__', '__main__'):
    AppNameApp(app_name='{project_name}').run_app()
