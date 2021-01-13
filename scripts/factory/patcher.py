"""Font patcher to add ligatures"""
import fontforge
import psMat
from .firacode import *

class Patcher(object):
    """Subclass to patch font file to add ligatures"""
    SINGLE_MAIN_LOOKUP = 'single.{}.{}'
    SINGLE_SUBTABLE_LOOKUP = 'single.{}.{}.1'
    EMPTY_GLYPH_NAME = 'empty.{}.{}'
    CONTEXTUAL_MAIN_LOOKUP = 'calt.{}'
    CONTEXTUAL_SUBTABLE_LOOKUP = 'calt.{}.{}'

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

            # Scale ligature font to em size of base font
            self.liga_font.em = self.base_font.em
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
        # Create a new character for ligature
        self.base_font.createChar(-1, ligature_name)
        self.base_font.selection.none()
        self.base_font.selection.select(ligature_name)
        self.base_font.paste()

        # Correct width
        self.correct_ligature_width(self.base_font[ligature_name])

    def correct_ligature_width(self, glyph):
        """Correct the horizontal advance and scale of a ligature.

        Args:
            glyph: (FontForge's glyph) Glyph of font
        """
        # Get max width of glyph that ligature must resize to, use m character
        max_width = self.base_font[ord('m')].width
        if glyph.width == max_width:
            return

        print('Correcting width from {}'.format(glyph.width))
        # Scale large ligature to standard size
        scale = float(max_width) / glyph.width
        glyph.transform(psMat.scale(scale, 1.0))
        glyph.width = max_width

    def create_single_lookup(self, input_chars, ligature_name):
        """
        Create FontForge lookup, for each segment of ligature from input chars.

        Args:
            input_chars: (list) A list of input characters.
            ligature_name: (string) Name of ligature in ligature font.
        """
        lookup_name = lambda i: Patcher.SINGLE_MAIN_LOOKUP \
            .format(ligature_name, i)
        subtable_name = lambda i: Patcher.SINGLE_SUBTABLE_LOOKUP \
            .format(ligature_name, i)
        spacer_name = lambda i: Patcher.EMPTY_GLYPH_NAME \
            .format(ligature_name, i)

        for i, char in enumerate(input_chars):
            self.base_font.addLookup(lookup_name(i), 'gsub_single', (), ())
            self.base_font.addLookupSubtable(lookup_name(i), subtable_name(i))

            if char not in self.base_font:
                # Add glyph for current char if base font doesn't have it
                self.base_font[ord(CHAR_DICT[char])].glyphname = char

            if i < len(input_chars) - 1:
                print('Adding empty glyph and replace rule for {}.{} char {}'\
                      .format(ligature_name, i, char))
                # Create an empty glyph for each segment of ligature,
                # exclude last char
                self.base_font.selection.none()
                self.base_font.selection.select('space')
                self.base_font.copy()

                self.base_font.createChar(-1, spacer_name(i))
                self.base_font.selection.none()
                self.base_font.selection.select(spacer_name(i))
                self.base_font.paste()

                # Add rule for replacement if match
                # from first to nearest last char of ligatures
                self.base_font[char].addPosSub(subtable_name(i),
                                               spacer_name(i))
            else:
                print('Adding replace rule for {}.{} char {}'\
                      .format(ligature_name, i, char))
                # Add rule for replacement if match last char of ligatures
                self.base_font[char].addPosSub(subtable_name(i), ligature_name)

    def create_matching_lookup(self, input_chars, ligature_name):
        """
        Create FontForge lookup, for matching rule from list of segment
        to generate ligature

        Args:
            input_chars: (list) A list of input characters.
            ligature_name: (string) Name of ligature in ligature font.
        """
        lookup_name = Patcher.CONTEXTUAL_MAIN_LOOKUP.format(ligature_name)
        single_lookup_name = lambda i: Patcher.SINGLE_MAIN_LOOKUP \
            .format(ligature_name, i)
        subtable_name = lambda i: Patcher.CONTEXTUAL_SUBTABLE_LOOKUP \
            .format(ligature_name, i)
        spacer_name = lambda i: Patcher.EMPTY_GLYPH_NAME \
            .format(ligature_name, i)
        prev_segment = lambda i: ' '.join(
            spacer_name(j) for j in range(i))
        next_segment = lambda i: ' '.join(input_chars[i+1:])

        self.base_font.addLookup(lookup_name, 'gsub_contextchain', (),
                            (('calt', (('DFLT', ('dflt')),
                                       ('latn', ('dflt')),
                                       ('math', ('dflt')))),))
        print('Adding CALT contextual with name %s' % (lookup_name))

        for i, char in enumerate(input_chars):
            # Add rule in subtable of lookup
            self.add_contextual_alternative(lookup_name, subtable_name(i),
                          '{prev} | {current} @<{lookup}> | {next}',
                          prev = prev_segment(i),
                          current = char,
                          lookup = single_lookup_name(i),
                          next = next_segment(i))

    def add_contextual_alternative(self, lookup_name, subtable_name,
                                   rule, kind='glyph', **kwargs):
        """Wrapper to creates a subtable within the specified contextual
        lookup for ligature.

        Args:
            lookup_name: (string) FontForge lookup name
            subtable_name: (string) FontForge subtable name
            rule: (string) Glyph rule to match that follow FontForge convention
            kind: (string) Type of addContextualSubtable of FontForge
        """
        rule = rule.format(**kwargs)
        print ('Subtable %s: %s' % (subtable_name, rule))
        self.base_font.addContextualSubtable(lookup_name, subtable_name,
                                             kind, rule)

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

        # Create FontForge lookup
        self.create_single_lookup(input_chars, ligature_name)
        self.create_matching_lookup(input_chars, ligature_name)

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
