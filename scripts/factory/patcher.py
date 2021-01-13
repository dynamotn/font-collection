"""Font patcher to add ligatures"""
import fontforge
from .firacode import LIGATURES

class Patcher(object):
    """Subclass to patch font file to add ligatures"""
    def __init__(self, base_font, liga_font):
        """
        Args:
            base_font: (string) Path of base font to create new font
            liga_font: (string) Path of ligature font that want to
                add ligatures to base font
        """
        try:
            self.base_font = fontforge.open(base_font)
            self.liga_font = fontforge.open(liga_font)
        except Exception as e:
            print('Exception while opening font file: {}'.format(e))
            raise

    def copy_ligature_from_source(self, ligature_name):
        """Copy ligature character from ligature font to FontForge's clipboard

        Args:
            ligature_name: (string) Name of ligature in ligature font.

        Returns:
            True/False: Success or not
        """
        try:
            self.liga_font.selection.none()
            self.liga_font.selection.select(ligature_name)
            self.liga_font.copy()
            return True
        except ValueError:
            return False

    def paste_ligature_to_destination(self, ligature_name):
        """Paste ligature character from FontForge's clipboard to base font

        Args:
            ligature_name: (string) Name of ligature in ligature font.
        """
        self.base_font.createChar(-1, ligature_name)
        self.base_font.selection.none()
        self.base_font.selection.select(ligature_name)
        self.base_font.paste()

    def add_ligature(self, input_chars, ligature_name):
        """Add ligature character & rules of it to base font that follow a
        sequence input characters by lookup from ligature font by ligature name.

        Args:
            input_chars: (list) A list of input characters.
            ligature_name: (string) Name of ligature in ligature font.
        """
        # Create a new character for ligature by copy and paste by FontForge
        if not self.copy_ligature_from_source(ligature_name):
            return
        self.paste_ligature_to_destination(ligature_name)

    def patch(self):
        """Patch font"""
        for spec in sorted(LIGATURES, key=lambda spec: len(spec['chars'])):
            try:
                print('Adding {}'.format(spec['name']))
                self.add_ligature(spec['chars'], spec['name'])
            except Exception as e:
                print('Exception while adding ligature: {}\n{}' \
                      .format(spec, e))
                raise
