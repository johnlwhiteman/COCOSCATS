# Contextually Correct Scatter Substitution (CoCoScatS)
### *A Mostly-Automated Content Generation Framework for Foreign Language Learning Plebes*


John L. Whiteman

## Description

My development track project supports grammar-free natural language learning where on-the-fly translations of foreign words and phrases are mixed with the native language in text. Here is an example of English words (the native language) "scatteredly" translated to Indonesian.

* I walked to the library yesterday to borrow a book about educational technology.

* ***Saya*** walked to the library ***kemarin*** to borrow a ***buku*** about ***pendidikan teknologi***.

The translations are word-for-word without regard to proper grammar structure in the foreign language. So in the example above, the correct translation for "educational technology" is not pendidikan teknologi, but rather teknologi pendidikan since adjectives in Indonesian come after nouns and not before them. Still this approach can be quite effective in regards to learning new vocabulary words so as long as they are translated in the right context. It is easy to build a tool that does the translations as long as it has access to a decent bilingual dictionary. It is hard though to ensure that the translations are contextually correct based on the content at hand. My project attempts to solve the following two problems: (1) generate contextually correct translations from content and (2) provide ways of presenting them back in the same content.

## Dependencies

* Python >= 3.6.0 (Highly recommend Anaconda >= 4.3.1)
  * [https://www.continuum.io/downloads]
  (https://www.continuum.io/downloads)
* A Microsoft Azure account with access to the Cognitive Services Language Translator if you want to use the Azure.py translator plugin

## Installation

* Download and install Python (see dependencies above)
* *git clone https://github.com/johnlwhiteman/CoCoScatS*
* *cd CoCoScatS*
* *python install*

## Execution

You can run Cocoscats from the command line or as a web application.

### - Command Mode

* *python ./run.py -C*

### - Web Mode

* *python ./run.py -W*

## Configuration File

This is a big TODO.