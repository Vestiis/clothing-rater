import difflib
import itertools
import logging
import multiprocessing
import os
from functools import lru_cache, partial
from typing import List, Sequence, Tuple, Union

import numpy as np
from nltk.tokenize import word_tokenize

from src.config import WordsMatcherConfig
from src.utils import chunks

logger = logging.getLogger(__name__)


class WordsMatcher:
    """The class in charge of finding in sentences the similar-looking words from a referential"""

    def __init__(
        self,
        similarity_type: str = "difflib",
        tokenization_type: str = "split",
        extract_with_multi_process: bool = False,
        similarity_threshold: float = 0.72,
    ):
        """
        :param similarity_type: The type of distance to use between strings (is one of "difflib")
        :param extract_with_multi_process: This indicates whether to parallelize computations over sentences
        :
        """
        self.similarity_type: str = similarity_type
        self.extract_with_multi_process: bool = extract_with_multi_process
        # a dictionary that maps a referential word to its standardized, tokenized, form
        # e.g "Hong Kong" becomes ["hong", "kong"]
        self.referential_words_as_tokens: dict = {}
        self.tokenization_type = tokenization_type
        self.tokenization_func = self._get_tokenization_func()
        self.similarity_threshold = similarity_threshold

    def _get_tokenization_func(self):
        if self.tokenization_type == "split":
            return lambda x: x.split(" ")
        if self.tokenization_type == "word_tokenize":
            return word_tokenize
        raise NotADirectoryError

    def tokenize(self, x: str):
        return self.tokenization_func(x)

    def top_similar_referential_word_per_sentence(
        self, sentences: Sequence[str], referential: Sequence[str],
    ) -> List[Union[str, None]]:
        (
            similar_referential_words_per_sentence,
            referential_words_scores_per_sentence,
        ) = self.similar_referential_words_per_sentence(sentences, referential)
        return [
            similar_referential_words_per_sentence[sentence_idx][
                np.argmax(referential_words_scores_per_sentence[sentence_idx])
            ]
            # if not empty
            if similar_referential_words_per_sentence[sentence_idx] else None
            for sentence_idx in range(len(sentences))
        ]

    def similar_referential_words_per_sentence(
        self, sentences: Sequence[str], referential: Sequence[str],
    ) -> Tuple[List[List[str]], List[List[float]]]:
        if not self.extract_with_multi_process:
            return self._similar_referential_words_per_sentence(
                sentences, self, referential
            )
        processes = multiprocessing.cpu_count()
        logger.info(
            f"Extraction of similar referential words has been required"
            f" with multiprocessing "
            f"number of available threads for multiprocess: {processes}"
        )
        pool = multiprocessing.Pool(processes=processes)
        words_referential_and_scores = pool.map(
            partial(
                self._similar_referential_words_per_sentence,
                words_matcher=self,
                referential=referential,
            ),
            chunks(elems=sentences, chunk_size=len(sentences) // processes),
        )
        pool.close()
        pool.join()
        similar_ref_words_per_sentence = list(
            itertools.chain(
                *[
                    ref_words_per_sentence
                    for (ref_words_per_sentence, _) in words_referential_and_scores
                ]
            )
        )
        similar_ref_words_scores_per_sentence = list(
            itertools.chain(
                *[
                    ref_words_scores_per_sentence
                    for (
                        _,
                        ref_words_scores_per_sentence,
                    ) in words_referential_and_scores
                ]
            )
        )
        return similar_ref_words_per_sentence, similar_ref_words_scores_per_sentence

    @staticmethod
    def _similar_referential_words_per_sentence(
        sentences: Sequence[str],
        words_matcher: "WordsMatcher",
        referential: Sequence[str],
    ) -> Tuple[List[List[str]], List[List[float]]]:
        similar_referential_words_per_sentence = []
        referential_words_scores_per_sentence = []
        for sentence in sentences:
            (
                similar_referential_words,
                referential_words_scores,
            ) = WordsMatcher._similar_referential_words_in_sentence(
                words_matcher, sentence, referential
            )
            similar_referential_words_per_sentence.append(similar_referential_words)
            referential_words_scores_per_sentence.append(referential_words_scores)
        return (
            similar_referential_words_per_sentence,
            referential_words_scores_per_sentence,
        )

    @staticmethod
    def _similar_referential_words_in_sentence(
        words_matcher: "WordsMatcher", sentence: str, referential: Sequence[str],
    ) -> Tuple[List[str], List[float]]:
        """Finds the referential words that are found in sentence with a similarity above some threshold parameter

        :param words_matcher: An instance of the WordsMatcher class
        :param sentence: The sentence in which to look for similar referential words
        :param referential: The group of words that are looked for in sentence
        :returns: A list of referential words found in sentence
        :returns: The list of the similarities scores of the referential words found in sentence
        """
        sentence_words = words_matcher.tokenize(
            words_matcher.standardize_word(sentence)
        )
        referential_words = []
        # standard_ref_words words might have been modified compared to ref_words words
        # e.g Make-Up standardized to make up
        standardized_referential_words = []
        all_subsentences = []
        for referential_word in referential:
            if referential_word == "Italie":
                print()
            # standardize to common spelling e.g L'Oréal to l'oreal
            standard_ref_word = words_matcher.standardize_word(referential_word)
            if standard_ref_word not in words_matcher.referential_words_as_tokens:
                words_matcher.referential_words_as_tokens[
                    standard_ref_word
                ] = words_matcher.tokenize(standard_ref_word)
            for n_grams in range(
                1,
                # for words like "République démocratique populaire lao",
                # generate all 1-grams, 2-grams, 3-grams and also 4-grams words
                # from sentence in case a bad split has resulted in a spelling error
                len(words_matcher.referential_words_as_tokens[standard_ref_word]) + 2,
            ):
                n_words_grams = words_matcher.n_grams_from_sentence_words(
                    sentence_words, n_grams=n_grams
                )
                all_subsentences += [
                    " ".join(n_words_gram) for n_words_gram in n_words_grams
                ]
                standardized_referential_words += [standard_ref_word] * len(
                    n_words_grams
                )
                referential_words += [referential_word] * len(n_words_grams)

        similarities_scores = words_matcher.similarities_from_word_pairs(
            list(zip(standardized_referential_words, all_subsentences)),
            words_matcher.similarity_type,
            multi_process=False,
        )
        similar_ref_words_idxs = np.where(
            np.array(similarities_scores) >= words_matcher.similarity_threshold
        )[0]
        return (
            [referential_words[idx] for idx in similar_ref_words_idxs],
            [similarities_scores[idx] for idx in similar_ref_words_idxs],
        )

    @staticmethod
    def standardize_word(word: str) -> str:
        word = str(word)
        # very important
        word = word.lower()
        # possibly remove ' or "
        word = word.replace(os.linesep, " ")
        word = word.lstrip()
        word = word.rstrip()
        word = word.replace("-", " ")
        word = word.replace("é", "e")
        word = word.replace("è", "e")
        return word.lower()

    @staticmethod
    def n_grams_from_sentence_words(
        sentence_words: List[str], n_grams: int
    ) -> List[List[str]]:
        return [
            sentence_words[i - n_grams : i]
            for i in range(n_grams, len(sentence_words) + 1)
        ]

    @staticmethod
    def _similarities_from_word_pairs(
        word_pairs: List[Tuple[str, str]], similarity_type: str
    ) -> List[float]:
        similarities_scores = [
            WordsMatcher.similarity(word1, word2, similarity_type)
            for word1, word2 in word_pairs
        ]
        return similarities_scores

    @staticmethod
    def similarities_from_word_pairs(
        word_pairs: List[Tuple[str, str]],
        similarity_type: str,
        multi_process: bool = True,
    ) -> List[float]:
        if not multi_process:
            return WordsMatcher._similarities_from_word_pairs(
                word_pairs, similarity_type
            )
        # processes = multiprocessing.cpu_count() - 1
        processes = multiprocessing.cpu_count()
        pool = multiprocessing.Pool(processes=processes)
        similarities = pool.map(
            partial(
                WordsMatcher._similarities_from_word_pairs,
                similarity_type=similarity_type,
            ),
            chunks(elems=word_pairs, chunk_size=len(word_pairs) // processes),
        )
        pool.close()
        pool.join()
        similarities = list(itertools.chain(*similarities))
        return similarities

    @staticmethod
    def similarity(ref_word: str, word: str, similarity_type: str) -> float:
        if similarity_type == "difflib":
            return difflib.SequenceMatcher(None, ref_word, word).ratio()
        else:
            raise NotImplementedError

    def top_similarity_from_word_pairs(
        self, word_pairs: List[Tuple[str, str]]
    ) -> Tuple[Tuple[str, str], float, int]:
        similarities_scores = self.similarities_from_word_pairs(
            word_pairs, self.similarity_type
        )
        top_pair_index = np.argmax(similarities_scores)
        return (
            word_pairs[top_pair_index],
            similarities_scores[top_pair_index],
            top_pair_index,
        )

    def closest_word_from_words(
        self, ref_word: str, words: Sequence[str]
    ) -> Tuple[str, float]:
        top_word_pair, top_similarity, _ = self.top_similarity_from_word_pairs(
            [(ref_word, word) for word in words]
        )
        ref_word, top_word = top_word_pair
        return top_word, top_similarity


# @lru_cache
def get_words_matcher():
    return WordsMatcher(
        similarity_type=WordsMatcherConfig.similarity_type,
        tokenization_type=WordsMatcherConfig.tokenization_type,
        extract_with_multi_process=WordsMatcherConfig.extract_with_multi_process,
        similarity_threshold=WordsMatcherConfig.similarity_threshold,
    )
