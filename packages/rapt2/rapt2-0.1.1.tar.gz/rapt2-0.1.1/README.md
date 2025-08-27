# RAPTv2

RAPT uses a syntactic and semantic understanding of RA to transform input
statements into a variety of outputs, including LATEX formatted queries,
parse tree diagrams, and executable SQL statements.

To use RAPT, create an instance of `rapt2.Rapt`, and use the desired methods.
Optionally, you can pass in keyword arguments that define the relational algebra
grammar and syntax. `config/default.json` contains an example.

## Acknowledgements

This is a fork of the now abandoned [pyrapt/rapt](https://github.com/pyrapt/rapt). All work preceeding 22/08/2025 should be attributed to the [original authors](https://github.com/pyrapt/rapt/blob/master/AUTHORS.rst)