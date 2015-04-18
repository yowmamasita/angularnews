# -*- coding: utf-8 -*-
"""So much practical programming involves string manipulation, which
Python readily accomodates. Still, there are dozens of basic and
common capabilities missing from the standard library, several of them
provided by ``strutils``.
"""

from __future__ import print_function

import re
import string
import unicodedata
import collections

try:
    unicode, str, bytes, basestring = unicode, str, str, basestring
except NameError:  # basestring not defined in Python 3
    unicode, str, bytes, basestring = str, bytes, bytes, str
    unichr = chr


__all__ = ['camel2under', 'under2camel', 'slugify', 'split_punct_ws',
           'unit_len', 'ordinalize', 'cardinalize', 'pluralize', 'singularize',
           'asciify', 'strip_ansi', 'bytes2human',
           'find_hashtags', 'a10n']  # 'StringBuffer']


_punct_ws_str = string.punctuation + string.whitespace
_punct_re = re.compile('[' + _punct_ws_str + ']+')
_camel2under_re = re.compile('((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def camel2under(camel_string):
    """Converts a camelcased string to underscores. Useful for turning a
    class name into a function name.

    >>> camel2under('BasicParseTest')
    'basic_parse_test'
    """
    return _camel2under_re.sub(r'_\1', camel_string).lower()


def under2camel(under_string):
    """Converts an underscored string to camelcased. Useful for turning a
    function name into a class name.

    >>> under2camel('complex_tokenizer')
    'ComplexTokenizer'
    """
    return ''.join(w.capitalize() or '_' for w in under_string.split('_'))


def slugify(text, delim='_', lower=True, ascii=False):
    """
    A basic function that turns text full of scary characters
    (i.e., punctuation and whitespace), into a relatively safe
    lowercased string separated only by the delimiter specified
    by *delim*, which defaults to ``_``.

    The *ascii* convenience flag will :func:`asciify` the slug if
    you require ascii-only slugs.

    >>> slugify('First post! Hi!!!!~1    ')
    'first_post_hi_1'

    # TODO: repr under Py3k
    # >>> slugify("Kurt Gödel's pretty cool.", ascii=True)
    # 'kurt_goedel_s_pretty_cool'

    >>> slugify("Kurt Gödel's pretty cool.", ascii=True) == \
        b'kurt_goedel_s_pretty_cool'
    True

    """
    ret = delim.join(split_punct_ws(text))
    if ascii:
        ret = asciify(ret)
    if lower:
        ret = ret.lower()
    return ret


def split_punct_ws(text):
    """While :meth:`str.split` will split on whitespace,
    :func:`split_punct_ws` will split on punctuation and
    whitespace. This used internally by :func:`slugify`, above.

    >>> split_punct_ws('First post! Hi!!!!~1    ')
    ['First', 'post', 'Hi', '1']
    """
    return [w for w in _punct_re.split(text) if w]


def unit_len(sized_iterable, unit_noun='item'):  # TODO: len_units()/unitize()?
    """Returns a plain-English description of an iterable's
    :func:`len()`, conditionally pluralized with :func:`cardinalize`,
    detailed below.

    >>> print(unit_len(range(10), 'number'))
    10 numbers
    >>> print(unit_len('aeiou', 'vowel'))
    5 vowels
    >>> print(unit_len([], 'worry'))
    No worries
    """
    count = len(sized_iterable)
    units = cardinalize(unit_noun, count)
    if count:
        return u'%s %s' % (count, units)
    return u'No %s' % (units,)


_ORDINAL_MAP = {'1': 'st',
                '2': 'nd',
                '3': 'rd'}  # 'th' is the default


def ordinalize(number, ext_only=False):
    """Turns *number* into its cardinal form, i.e., 1st, 2nd,
    3rd, 4th, etc. If the last character isn't a digit, it returns the
    string value unchanged.

    Args:
        number (int or str): Number to be cardinalized.
        ext_only (bool): Whether to return only the suffix. Default ``False``.

    >>> print(ordinalize(1))
    1st
    >>> print(ordinalize(3694839230))
    3694839230th
    >>> print(ordinalize('hi'))
    hi

    """
    numstr = unicode(number)
    rdig, ext = numstr[-1:], ''
    if not rdig:
        return ''
    if rdig in string.digits:
        ext = _ORDINAL_MAP.get(rdig, 'th')
    if ext_only:
        return ext
    else:
        return numstr + ext


def cardinalize(unit_noun, count):
    """Conditionally pluralizes a singular word *unit_noun* if
    *count* is not one, preserving case when possible.

    >>> vowels = 'aeiou'
    >>> print(len(vowels), cardinalize('vowel', len(vowels)))
    5 vowels
    >>> print(3, cardinalize('Wish', 3))
    3 Wishes
    """
    if count == 1:
        return unit_noun
    return pluralize(unit_noun)


def singularize(word):
    """Semi-intelligently converts an English plural *word* to its
    singular form, preserving case pattern.

    >>> singularize('records')
    'record'
    >>> singularize('FEET')
    'FOOT'

    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_S2P:
        return orig_word

    irr_singular = _IRR_P2S.get(word)
    if irr_singular:
        singular = irr_singular
    elif not word.endswith('s'):
        return orig_word
    elif len(word) == 2:
        singular = word[:-1]  # or just return word?
    elif word.endswith('ies') and word[-5:-4] not in 'aeiou':
        singular = word[:-3] + 'y'
    elif word.endswith('es'):
        singular = word[:-2]
    else:
        singular = word[:-1]
    return _match_case(orig_word, singular)


def pluralize(word):
    """Semi-intelligently converts an English *word* from singular form to
    plural, preserving case pattern.

    >>> pluralize('friend')
    'friends'
    >>> pluralize('enemy')
    'enemies'
    >>> pluralize('Sheep')
    'Sheep'
    """
    orig_word, word = word, word.strip().lower()
    if not word or word in _IRR_P2S:
        return orig_word
    irr_plural = _IRR_S2P.get(word)
    if irr_plural:
        plural = irr_plural
    elif word.endswith('y') and word[-2:-1] not in 'aeiou':
        plural = word[:-1] + 'ies'
    elif word[-1] == 's' or word.endswith('ch') or word.endswith('sh'):
        plural = word if word.endswith('es') else word + 'es'
    else:
        plural = word + 's'
    return _match_case(orig_word, plural)


def _match_case(master, disciple):
    if not master.strip():
        return disciple
    if master.lower() == master:
        return disciple.lower()
    elif master.upper() == master:
        return disciple.upper()
    elif master.capitalize() == master:
        return disciple.capitalize()
    return disciple


# Singular to plural map of irregular pluralizations
_IRR_S2P = {'alumnus': 'alumni', 'analysis': 'analyses', 'antenna': 'antennae',
            'appendix': 'appendices', 'axis': 'axes', 'bacterium': 'bacteria',
            'basis': 'bases', 'beau': 'beaux', 'bureau': 'bureaus',
            'cactus': 'cacti', 'child': 'children', 'corpus': 'corpora',
            'crisis': 'crises', 'criterion': 'criteria',
            'curriculum': 'curricula', 'datum': 'data', 'deer': 'deer',
            'diagnosis': 'diagnoses', 'ellipsis': 'ellipses', 'fish': 'fish',
            'focus': 'foci', 'foot': 'feet', 'formula': 'formulae',
            'fungus': 'fungi', 'genus': 'genera', 'goose': 'geese',
            'hypothesis': 'hypotheses', 'index': 'indeces', 'louse': 'lice',
            'man': 'men', 'matrix': 'matrices', 'means': 'means',
            'medium': 'media', 'memorandum': 'memoranda', 'mouse': 'mice',
            'nebula': 'nebulae', 'nucleus': 'nuclei', 'oasis': 'oases',
            'offspring': 'offspring', 'ox': 'oxen', 'paralysis': 'paralyses',
            'parenthesis': 'parentheses', 'phenomenon': 'phenomena',
            'radius': 'radii', 'series': 'series', 'sheep': 'sheep',
            'species': 'species', 'stimulus': 'stimuli', 'stratum': 'strata',
            'synopsis': 'synopses', 'synthesis': 'syntheses',
            'tableau': 'tableaux', 'thesis': 'theses', 'tooth': 'teeth',
            'vertebra': 'vertebrae', 'vita': 'vitae', 'woman': 'women'}


# Reverse index of the above
_IRR_P2S = dict([(v, k) for k, v in _IRR_S2P.items()])

HASHTAG_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)", re.UNICODE)


def find_hashtags(string):
    """Finds and returns all hashtags in a string, with the hashmark
    removed. Supports full-width hashmarks for Asian languages and
    does not false-positive on URL anchors.

    >>> find_hashtags('#atag http://asite/#ananchor')
    ['atag']

    ``find_hashtags`` also works with unicode hashtags.
    """

    # the following works, doctest just struggles with it
    # >>> find_hashtags(u"can't get enough of that dignity chicken #肯德基 woo")
    # [u'\u80af\u5fb7\u57fa']
    return HASHTAG_RE.findall(string)


def a10n(string):
    """That thing where "internationalization" becomes "i18n", what's it
    called? Abbreviation? Oh wait, no: ``a10n``. (It's actually a form
    of `numeronym`_.)

    >>> a10n('abbreviation')
    'a10n'
    >>> a10n('internationalization')
    'i18n'
    >>> a10n('')
    ''

    .. _numeronym: http://en.wikipedia.org/wiki/Numeronym
    """
    if len(string) < 3:
        return string
    return '%s%s%s' % (string[0], len(string[1:-1]), string[-1])


class StringBuffer(object):
    """
    This is meant to be a better file-like string buffer.
    Faster than StringIO, better encoding handling than cStringIO.

    This one is for unicode text strings. Look for ByteBuffer if you
    want to handle byte strings.

    (NOTE: not quite done yet)
    """
    def __init__(self, default_encoding=None, errors='strict'):
        self.data = collections.deque()
        self.default_encoding = default_encoding or 'utf-8'
        self.errors = errors

    def write(self, s):
        if not isinstance(s, unicode):
            enc = self.default_encoding
            errs = self.errors
            try:
                s = s.decode(enc, errs)
            except AttributeError:
                raise ValueError('write() expected a unicode or byte string')
        self.data.append(s)

    def truncate(self):
        self.data = collections.deque()
        self.write = self.data.append

    def getvalue(self):
        return unicode().join(self.data)

ANSI_ESCAPE_BEGIN = '\x1b['
ANSI_TERMINATORS = ('H', 'f', 'A', 'B', 'C', 'D', 'R', 's', 'u', 'J',
                    'K', 'h', 'l', 'p', 'm')


def strip_ansi(text):
    """Strips ANSI escape codes from *text*. Useful for the occasional
    time when a log or redirected output accidentally captures console
    color codes and the like.

    >>> strip_ansi('\x1b[0m\x1b[1;36mart\x1b[46;34m\xdc')
    'art'

    The test above is an excerpt from ANSI art on
    `sixteencolors.net`_. This function does not interpret or render
    ANSI art, but you can do so with `ansi2img`_ or `escapes.js`_.

    .. _sixteencolors.net: http://sixteencolors.net
    .. _ansi2img: http://www.bedroomlan.org/projects/ansi2img
    .. _escapes.js: https://github.com/atdt/escapes.js
    """
    # TODO: move to cliutils.py
    nansi, keep, i, text_len = [], True, 0, len(text)
    while i < text_len:
        if not keep and text[i] in ANSI_TERMINATORS:
            keep = True
        elif keep:
            keep_end_i = text.find(ANSI_ESCAPE_BEGIN, i)
            if keep_end_i < 0:
                break
            else:
                nansi.append(text[i:keep_end_i])
                i, keep = keep_end_i, False
        i += 1
    if not nansi:
        return text
    return type(text)().join(nansi)  # attempted unicode + str support


def asciify(text, ignore=False):
    """Converts a unicode or bytestring, *text*, into a bytestring with
    just ascii characters. Performs basic deaccenting for all you
    Europhiles out there.

    Also, a gentle reminder that this is a **utility**, primarily meant
    for slugification. Whenever possible, make your application work
    **with** unicode, not against it.

    Args:
        text (str or unicode): The string to be asciified.
        ignore (bool): Configures final encoding to ignore remaining
            unasciified unicode instead of replacing it.

    # TODO: repr under Py3k
    # >>> asciify('Beyoncé')
    # 'Beyonce'

    >>> asciify('Beyoncé') == b'Beyonce'
    True

    """
    # TODO: Python 3 compliance.
    try:
        try:
            return text.encode('ascii')
        except UnicodeDecodeError:
            # this usually means you passed in a non-unicode string
            text = text.decode('utf-8')
            return text.encode('ascii')
    except UnicodeEncodeError:
        mode = 'replace'
        if ignore:
            mode = 'ignore'
        transd = unicodedata.normalize('NFKD', text.translate(DEACCENT_MAP))
        ret = transd.encode('ascii', mode)
        return ret


class DeaccenterDict(dict):
    "A small caching dictionary for deaccenting."
    def __missing__(self, key):
        ch = self.get(key)
        if ch is not None:
            return ch
        try:
            de = unicodedata.decomposition(unichr(key))
            p1, _, p2 = de.rpartition(' ')
            if int(p2, 16) == 0x308:
                ch = self.get(key)
            else:
                ch = int(p1, 16)
        except (IndexError, ValueError):
            ch = self.get(key, key)
        self[key] = ch
        return ch

    try:
        from collections import defaultdict
    except ImportError:
        # no defaultdict means that __missing__ isn't supported in
        # this version of python, so we define __getitem__
        def __getitem__(self, key):
            try:
                return super(DeaccenterDict, self).__getitem__(key)
            except KeyError:
                return self.__missing__(key)
    else:
        del defaultdict


# http://chmullig.com/2009/12/python-unicode-ascii-ifier/
# For something more complete, investigate the unidecode
# or isounidecode packages, which are capable of performing
# crude transliteration.
_BASE_DEACCENT_MAP = {
    0xc6: u"AE", # Æ LATIN CAPITAL LETTER AE
    0xd0: u"D",  # Ð LATIN CAPITAL LETTER ETH
    0xd8: u"OE", # Ø LATIN CAPITAL LETTER O WITH STROKE
    0xde: u"Th", # Þ LATIN CAPITAL LETTER THORN
    0xc4: u'Ae', # Ä LATIN CAPITAL LETTER A WITH DIAERESIS
    0xd6: u'Oe', # Ö LATIN CAPITAL LETTER O WITH DIAERESIS
    0xdc: u'Ue', # Ü LATIN CAPITAL LETTER U WITH DIAERESIS
    0xc0: u"A",  # À LATIN CAPITAL LETTER A WITH GRAVE
    0xc1: u"A",  # Á LATIN CAPITAL LETTER A WITH ACUTE
    0xc3: u"A",  # Ã LATIN CAPITAL LETTER A WITH TILDE
    0xc7: u"C",  # Ç LATIN CAPITAL LETTER C WITH CEDILLA
    0xc8: u"E",  # È LATIN CAPITAL LETTER E WITH GRAVE
    0xc9: u"E",  # É LATIN CAPITAL LETTER E WITH ACUTE
    0xca: u"E",  # Ê LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    0xcc: u"I",  # Ì LATIN CAPITAL LETTER I WITH GRAVE
    0xcd: u"I",  # Í LATIN CAPITAL LETTER I WITH ACUTE
    0xd2: u"O",  # Ò LATIN CAPITAL LETTER O WITH GRAVE
    0xd3: u"O",  # Ó LATIN CAPITAL LETTER O WITH ACUTE
    0xd5: u"O",  # Õ LATIN CAPITAL LETTER O WITH TILDE
    0xd9: u"U",  # Ù LATIN CAPITAL LETTER U WITH GRAVE
    0xda: u"U",  # Ú LATIN CAPITAL LETTER U WITH ACUTE
    0xdf: u"ss", # ß LATIN SMALL LETTER SHARP S
    0xe6: u"ae", # æ LATIN SMALL LETTER AE
    0xf0: u"d",  # ð LATIN SMALL LETTER ETH
    0xf8: u"oe", # ø LATIN SMALL LETTER O WITH STROKE
    0xfe: u"th", # þ LATIN SMALL LETTER THORN,
    0xe4: u'ae', # ä LATIN SMALL LETTER A WITH DIAERESIS
    0xf6: u'oe', # ö LATIN SMALL LETTER O WITH DIAERESIS
    0xfc: u'ue', # ü LATIN SMALL LETTER U WITH DIAERESIS
    0xe0: u"a",  # à LATIN SMALL LETTER A WITH GRAVE
    0xe1: u"a",  # á LATIN SMALL LETTER A WITH ACUTE
    0xe3: u"a",  # ã LATIN SMALL LETTER A WITH TILDE
    0xe7: u"c",  # ç LATIN SMALL LETTER C WITH CEDILLA
    0xe8: u"e",  # è LATIN SMALL LETTER E WITH GRAVE
    0xe9: u"e",  # é LATIN SMALL LETTER E WITH ACUTE
    0xea: u"e",  # ê LATIN SMALL LETTER E WITH CIRCUMFLEX
    0xec: u"i",  # ì LATIN SMALL LETTER I WITH GRAVE
    0xed: u"i",  # í LATIN SMALL LETTER I WITH ACUTE
    0xf2: u"o",  # ò LATIN SMALL LETTER O WITH GRAVE
    0xf3: u"o",  # ó LATIN SMALL LETTER O WITH ACUTE
    0xf5: u"o",  # õ LATIN SMALL LETTER O WITH TILDE
    0xf9: u"u",  # ù LATIN SMALL LETTER U WITH GRAVE
    0xfa: u"u",  # ú LATIN SMALL LETTER U WITH ACUTE
    0x2018: u"'",  # ‘ LEFT SINGLE QUOTATION MARK
    0x2019: u"'",  # ’ RIGHT SINGLE QUOTATION MARK
    0x201c: u'"',  # “ LEFT DOUBLE QUOTATION MARK
    0x201d: u'"',  # ” RIGHT DOUBLE QUOTATION MARK
    }


DEACCENT_MAP = DeaccenterDict(_BASE_DEACCENT_MAP)


_SIZE_SYMBOLS = ('B', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
_SIZE_BOUNDS = [(1024 ** i, sym) for i, sym in enumerate(_SIZE_SYMBOLS)]
_SIZE_RANGES = list(zip(_SIZE_BOUNDS, _SIZE_BOUNDS[1:]))


def bytes2human(nbytes, ndigits=0):
    """Turns an integer value of *nbytes* into a human readable format. Set
    *ndigits* to control how many digits after the decimal point
    should be shown (default ``0``).

    >>> bytes2human(128991)
    '126K'
    >>> bytes2human(100001221)
    '95M'
    >>> bytes2human(0, 2)
    '0.00B'
    """
    abs_bytes = abs(nbytes)
    for (size, symbol), (next_size, next_symbol) in _SIZE_RANGES:
        if abs_bytes <= next_size:
            break
    hnbytes = float(nbytes) / size
    return '{hnbytes:.{ndigits}f}{symbol}'.format(hnbytes=hnbytes,
                                                  ndigits=ndigits,
                                                  symbol=symbol)


if __name__ == '__main__':
    b = asciify(u'Beyoncé')
    print(ord(unicode(b)[-1]))
    print(b)
    print(DEACCENT_MAP)
