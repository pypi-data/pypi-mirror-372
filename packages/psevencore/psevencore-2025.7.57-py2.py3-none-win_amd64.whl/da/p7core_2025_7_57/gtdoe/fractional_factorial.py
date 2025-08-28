#
# coding: utf-8
# Copyright (C) pSeven SAS, 2010-present
#
from __future__ import division

import numpy as np

from .. import exceptions as _ex
from ..six.moves import xrange, range, zip
from ..utils import bit_length

_ALPHABET='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def _generate_fractional_factorial(bounds, points_number, categorical_variables, generating_string, main_factors, sift_logger, validation_mode=False):
  """
  Generate a Fractional Factorial DoE with Python.

  :param bounds: design space bounds
  :type bounds: ``tuple(list(float), list(float))``
  :param points_number: number of points to generate)
  :type points_number: ``int``, ``long``
  :param categorical_variables: list of pairs (not tuples): 0-based index of categorical variable followed by list of categorical levels
  :type categorical_variables: ``list``
  :param generating_string: generating sring for fractional factorial
  :type generating_string: ``string``
  :param main_factors: main factors for fractional factorial
  :type main_factors: ``string`` with a list of ints
  :param logger: :ref:`logger <Logger>` object
  :return: points
  :rtype: numpy.ndarray
  """
  points_number = 0 if points_number is None else int(points_number)
  if points_number < 0:
    raise ValueError("The number of points is invalid: %s" % (points_number,))

  factors_number = len(bounds[0])

  levels = get_two_levels(bounds, list(categorical_variables), sift_logger)
  max_points_number = np.power(2, factors_number)

  if points_number and max_points_number < points_number:
    sift_logger.warn("Fractional Factorial design cannot include more points than two to the power of the number of variables: " +\
                    "%d points will be generated, %d points were requested." % (max_points_number, points_number))
    points_number = max_points_number

  if points_number == 0:
    if np.shape(main_factors)[0] == 0:
      # Minimum valid number of main factors to get minimum valid number of points (should be more than factors_number + 1)
      required_main_factors_number = int(np.ceil(np.log2(factors_number + 1)))
    else:
      required_main_factors_number = len(set(main_factors))
    points_number = np.power(2, required_main_factors_number)
  else:
    required_main_factors_number = bit_length.get_floored_binary_logarithm(points_number)

    if np.power(2, required_main_factors_number) != points_number:
      points_number = int(np.power(2, required_main_factors_number))
      sift_logger.warn("Fractional factorial design always includes power of 2 points. The updated number of points to generate is " + str(points_number) + ".")

  if np.power(2, required_main_factors_number) < factors_number + 1:
    raise _ex.InvalidProblemError("It is impossible to generate fractional factorial design with the given parameters. Try to increase points count or number of main factors.")

  if (generating_string == "") or (not is_generating_string_correct(factors_number, generating_string, main_factors, sift_logger)):
    generating_string = generate_generating_string(factors_number, required_main_factors_number, sift_logger, main_factors)

  if validation_mode:
    return {}, np.empty((points_number, 0))

  info = {"Generator": {"FractionalFactorialOptions": {"GeneratingString": str(generating_string)}}}

  unique_characters = list(set(generating_string))
  words = generating_string.split(" ")
  for word_number in xrange(len(words) - 1, -1, -1):
    if words[word_number] == '':
      del words[word_number]
  one_letter_words = [element for element in words if len(element) == 1]
  unique_alpha = []
  for character_number in xrange(len(unique_characters)):
    if unique_characters[character_number].isalpha():
      unique_alpha[len(unique_alpha):] = unique_characters[character_number]

  entries = [dict((key, False) for key in unique_alpha) for _ in xrange(factors_number)]
  for word_number in xrange(factors_number):
    for letter in words[word_number]:
      if letter in one_letter_words:
        entries[word_number][letter] = True

  full_factorial_for_main = np.zeros((points_number, required_main_factors_number))
  level_repeat = 1
  range_repeat = int(np.power(2, required_main_factors_number))
  for main_factor_number in range(required_main_factors_number):
    range_repeat //= 2
    subcolumn = []
    for level in [-1, 1]:
      subcolumn += [level] * level_repeat
    column = subcolumn * range_repeat
    level_repeat *= 2
    full_factorial_for_main[:, main_factor_number] = column

  points = np.ones((points_number, factors_number))
  number_of_entries = [0]*factors_number
  for factor_number in xrange(factors_number):
    for letter_number in xrange(len(unique_alpha)):
      if entries[factor_number][unique_alpha[letter_number]]:
        number_of_entries[factor_number] = number_of_entries[factor_number] + 1
        for point_number in xrange(points_number):
          points[point_number, factor_number] *= full_factorial_for_main[point_number, letter_number]

  points = reconstruct_levels(points, levels, sift_logger)
  info["Generator"]["FractionalFactorialOptions"]["MainFactors"] = np.where(np.array(number_of_entries) == 1)[0].tolist()

  return info, points

def get_two_levels(bounds, categorical_variables, sift_logger):
  """
  Get two levels for each factor.

  :param bounds: design space bounds
  :type bounds: ``tuple(list(float), list(float))``
  :param logger: :ref:`logger <Logger>` object
  :return: levels
  :rtype: ``numpy.ndarray``
  """

  factors_number = len(bounds[0])
  levels = np.zeros((factors_number, 2))
  for factor_number in xrange(factors_number):
    levels[factor_number, 0] = bounds[0][factor_number]
    levels[factor_number, 1] = bounds[1][factor_number]
  for catvar_index, catvar_levels in zip(categorical_variables[0::2], categorical_variables[1::2]):
    number_levels = len(catvar_levels)
    if number_levels == 2:
      levels[catvar_index, 0] = catvar_levels[0]
      levels[catvar_index, 1] = catvar_levels[1]
    elif number_levels > 1:
      raise _ex.InvalidProblemError("Categorical factor " + str(catvar_index) +
                                    " from 'GTDoE/CategorialVariables' contains " + str(number_levels) +
                                    " levels. But all factors must contain either 1 or 2 levels.")
  return levels

def reconstruct_levels(points, levels, sift_logger):
  """
  Map from {-1, +1} to the initial levels for each factor.

  :param points: 2D-array with values from {-1, +1}
  :type points: ``numpy.ndarray``
  :param levels: initial levels
  :type levels: ``numpy.ndarray``
  :param logger: :ref:`logger <Logger>` object
  :return: points
  :rtype: numpy.ndarray
  """

  for factor_number in xrange(np.shape(points)[1]):
    for point_number in xrange(np.shape(points)[0]):
      if (points[point_number, factor_number] == -1):
        points[point_number, factor_number] = levels[factor_number, 0]
      elif (points[point_number, factor_number] == 1):
        points[point_number, factor_number] = levels[factor_number, 1]
  return points

def is_generating_string_correct(factors_number, generating_string, main_factors, sift_logger):
  """
  Check if generating string is correct.

  :param factors_number: number of factors
  :type points: ``int``
  :param generating_string: generating string for fractional factorial
  :type generating_string: ``string``
  :param main_factors: main factors for fractional factorial
  :type main_factors: ``numpy.ndarray``
  :param logger: :ref:`logger <Logger>` object
  :return: is_correct
  :rtype: ``bool``
  """

  main_factors = np.array(main_factors)

  unique_characters = list(set(generating_string))
  words = generating_string.split(" ")
  one_letter_words = [element for element in words if len(element) == 1]

  if len(words) != factors_number:
    raise _ex.InvalidOptionValueError("Error when setting option 'GTDoE/FractionalFactorial/GeneratingString'. " +
                                      "The number of words in generating string is not equal to the number of factors.")

  unique_alpha = []
  for character_number in xrange(len(unique_characters)):
    if unique_characters[character_number].isalpha():
      unique_alpha[len(unique_alpha):] = unique_characters[character_number]
    elif unique_characters[character_number] != " ":
      raise _ex.InvalidOptionValueError("Error when setting option 'GTDoE/FractionalFactorial/GeneratingString'. " +
                                        "Generating string contains prohibited characters.")

  entries = [dict((key, False) for key in unique_alpha) for _ in xrange(factors_number)]
  for word_number in xrange(factors_number):
    for letter in words[word_number]:
      if letter in one_letter_words:
        if entries[word_number][letter] == False:
          entries[word_number][letter] = True
        else:
          raise _ex.InvalidOptionValueError("Error when setting option 'GTDoE/FractionalFactorial/GeneratingString'. " +
                                            "Some words have repeated letters.")
      else:
        raise _ex.InvalidOptionValueError("Error when setting option 'GTDoE/FractionalFactorial/GeneratingString'. " +
                                          "Generating string contains words with letters which are not from main factors.")
  if len(main_factors == 0):
    for word_number in xrange(factors_number):
      if len(words[word_number]) == 1 and word_number not in main_factors:
        raise _ex.InvalidProblemError("Options 'GTDoE/FractionalFactorial/GeneratingString' and 'GTDoE/FractionalFactorial/MainFactors' contradict: word '" +
                                      words[word_number] + "' of main factor " + str(word_number) + " contains more than one letter.")
      elif len(words[word_number]) > 1 and word_number in main_factors:
        raise _ex.InvalidProblemError("Options 'GTDoE/FractionalFactorial/GeneratingString' and 'GTDoE/FractionalFactorial/MainFactors' contradict: word '" +
                                      words[word_number] + "' does not set main factor " + str(word_number) + ".")

  for first_word_number in xrange(factors_number):
    for second_word_number in xrange(first_word_number):
      if set(words[first_word_number]) == set(words[second_word_number]):
        raise _ex.InvalidOptionValueError("Error when setting option 'GTDoE/FractionalFactorial/GeneratingString'. " +
                                          "Generating string contains equivalent words.")

  return True

def generate_generating_string(factors_number, main_factors_number, logger, main_factors=[]):
  """
  Generate correct generating string.

  :param factors_number: number of factors
  :type points: ``int``
  :param main_factors_number: number of main factors
  :type main_factors_number: ``int``, ``long``
  :param main_factors: main factors for fractional factorial
  :type main_factors: ``string`` with a list of ints
  :param logger: :ref:`logger <Logger>` object
  :return: generating_string
  :rtype: ``string``
  """
  main_factors = np.array(main_factors)
  if np.shape(main_factors)[0] == 0:
    main_factors = list(range(main_factors_number))
  else:
    unique_numbers = list(set(main_factors))
    if not ((len(unique_numbers) == main_factors_number) and all(main_factors < factors_number) and all(main_factors >= 0)):
      raise _ex.InvalidProblemError("Option 'GTDoE/FractionalFactorial/MainFactors' is not correct.")
  generating_string = ""
  number_processed_main_factors = 0
  current_long_word_number = main_factors_number + 1
  for current_factor in xrange(factors_number):
    if current_factor in main_factors:
      generating_string = generating_string + ' ' + get_letter_by_number(number_processed_main_factors)
      number_processed_main_factors = number_processed_main_factors + 1
    else:
      search_for_new_word = True
      while search_for_new_word:
        word = get_word_by_number(current_long_word_number, main_factors_number)
        if is_letter_sequence_increasing(word):
          search_for_new_word = False
        current_long_word_number = current_long_word_number + 1

      generating_string = generating_string + ' ' + word
  return generating_string[1:] # skip first white space

def get_next_letter(letter, letters_in_use):
  """
  Get next letter.

  :param letter: current letter
  :type letter: ``char``
  :param letters_in_use: number of letters in use (<=52)
  :type letters_in_use: ``int``
  :return: next_letter
  :rtype: ``char``
  """

  try:
    return _ALPHABET[(_ALPHABET.index(letter) + 1) % len(_ALPHABET)]
  except ValueError:
    # unknown letter try to get the next one using the number of letters used
    return _ALPHABET[(letters_in_use + 1) % len(_ALPHABET)]

def get_letter_by_number(number):
  """
  Get letter by its number in alphabet.

  :param number: order number of the letter (<52)
  :type number: ``int``
  :return: letter
  :rtype: ``char``

  """
  return _ALPHABET[number % len(_ALPHABET)]

def get_word_by_number(number, letters_in_use):
  """
  Get word by its number.

  :param number: order number of the word
  :type number: ``int``
  :param letters_in_use: number of letters in use (<=52)
  :type letters_in_use: ``int``
  :return: word
  :rtype: ``string``

  """
  result = ''
  letters_in_use += 1
  while number >= letters_in_use:
    result = _ALPHABET[max((number % letters_in_use) - 1, 0) % len(_ALPHABET)] + result
    number //= letters_in_use
  return _ALPHABET[max(number - 1, 0) % len(_ALPHABET)] + result

def get_letter_order_number(letter):
  """
  Get letter by its number in alphabet.

  :param letter: lower or upper case letter
  :type letter: ``char``
  :return: char_number
  :rtype: ``int``

  """

  try:
    return _ALPHABET.index(letter)
  except ValueError:
    return 0

def is_letter_sequence_increasing(word):
  """
  Check if the letters in letter sequence are decreasing ordered.

  :param word: word consists of lower or upper case letters
  :type word: ``string``
  :return: is_increasing
  :rtype: ``bool``
  """
  return all(_ALPHABET.index(l) < _ALPHABET.index(r) for l, r in zip(word[:-1], word[1:]))
