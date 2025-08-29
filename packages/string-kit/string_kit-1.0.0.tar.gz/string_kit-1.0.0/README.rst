.. |pypi-version| image:: https://img.shields.io/pypi/v/string-kit?label=PyPI%20Version&color=4BC51D
   :alt: PyPI Version
   :target: https://pypi.org/projects/string-kit/

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/string-kit?label=PyPI%20Downloads&color=037585
   :alt: PyPI Downloads
   :target: https://pypi.org/projects/string-kit/

string-kit
##########

|pypi-version| |pypi-downloads|

Description
***********

Provides advanced string utilities and a powerful Formatter.

Formatter
==============

``string_kit.Formatter`` is a drop-in replacement of ``string.Formatter`` and supports the same syntax and more.

``string_kit.Formatter`` adds the following features:
 - virtual fields ``now``, ``uuid1``, ``uuid4``, ``uuid5`` (no key is required in the format parameters, however if present, they take precedence); many more coming up.
 - user-defined virtual fields can be added through ``field_default`` init parm.
 - can send namespaces where format field values are searched through ``namespaces`` init parm.
 - ``!capitalize``, ``!lower``, ``!lstrip``, ``!rstrip``, ``!slug``, ``!strip``, ``!title``, ``!upper``; many more coming up.
 - user-defined convertors can be added through ``convertors`` init parm.
 - chained conversions and format specifications in any order: ``{field!slug:.10s!upper}``.
 - user-configurable ``silence_missing_fields``, if set ``True``, will suppress ``IndexError`` and ``KeyError`` and will quietly replace with empty string.
 - user-configurable characters to identify fields (default ``{}``), convertors (default ``!``) and format specifiers (default ``:``).

A simple example:

.. code-block:: python

   import random
   from string_kit import Formatter

   the_weather = "Sunny but Humid"

   custom_field_defaults = {
       "password": lambda: random.choice(["lI0n", "rAbb1t", "tig3R"]) \
                           + str(random.randint(1000, 9999)),
   }

   custom_convertors = {
       "greeting": lambda str_, greeting: f"{greeting} {str_}",
   }


   class CustomFormatter(Formatter):
       field_defaults = {
           "bye": "Good bye!",
       }
       convertors = {
           "space2dash": lambda str_: str_.replace(" ", "-")
       }


   skf = CustomFormatter(
       silence_missing_fields=True,
       field_defaults=custom_field_defaults,  # optional, dict with str or callable values
       convertors=custom_convertors,          # optional, dict with callable values
       field_namespaces=[locals()],           # optional, namespaces to search for field names
   )

   print(skf.format("{name!space2dash!greeting(Hello)},"
                    " your random password is: '{password}'. {bye}",
                    name="Charlie Brown"))
   # "Hello Charlie-Brown, your random password is: 'rAbb1t1258'. Good bye!"

   print(skf.format("Today is {now!strftime(%A)!upper}, also a"
                    " {the_weather!lower:.5!replace(sunny,sunny \\(☀️\\))} day."
                    " {missing!lstrip}"))
   # "Today is FRIDAY, also a sunny (☀️) day. "

Some TODO Ideas
===============

 - add ``snake_case``, ``kebab-case``, ``PascalCase``, ``camelCase`` as built-in convertors
 - add ``sqids`` convertor with parameters (strings allowed, length) passed as static values

Note: This is an alpha version, and things may change quite a bit.