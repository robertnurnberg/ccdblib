# Library with wrapper functions for the Chinese chessdb.cn API

The library `cdblib.py` allows to conveniently use the API of the Chinese Chess Cloud Database [chessdb.cn](https://chessdb.cn/query_en/) (ccdb), the largest online database of Chinese chess positions and openings, from within Python.

## This repo is work in progress ...

## Purpose

Provide a simple library with wrapper functions for the API of ccdb. All the wrapper functions will continuously query ccdb until a satisfactory response has been received.

## Usage

By way of example, one small application script is provided.

* [`fens2ccdb`](#fens2ccdb) - request evaluations from ccdb for FENs stored in a file

## Installation

```shell
git clone https://github.com/robertnurnberg/ccdblib && git clone https://github.com/windshadow233/python-chinese-chess && pip install -r ccdblib/requirements.txt
```

---

### `fens2ccdb`

A command line program to bulk-request evaluations from ccdb for all the FENs/EPDs stored within a file.

```
usage: fens2ccdb.py [-h] [--shortFormat] [--quiet] [-c CONCURRENCY] [-b BATCHSIZE] [-u USER] input [output]

A simple script to request evals from Chinese chessdb.cn for a list of FENs stored in a file. The script will add "; EVALSTRING;" to every line containing a FEN. Lines beginning with "#" are ignored, as well as any text after the first four fields of each FEN.

positional arguments:
  input                 source filename with FENs (w/ or w/o move counters)
  output                optional destination filename (default: None)

options:
  -h, --help            show this help message and exit
  --shortFormat         EVALSTRING will be just a number, or an "M"-ply mate score, or "#" for checkmate, or "". (default: False)
  --quiet               Suppress all unnecessary output to the screen. (default: False)
  -c CONCURRENCY, --concurrency CONCURRENCY
                        Maximum concurrency of requests to cdb. (default: 16)
  -b BATCHSIZE, --batchSize BATCHSIZE
                        Number of FENs processed in parallel. Small values guarantee more responsive output, large values give faster turnaround. (default: None)
  -u USER, --user USER  Add this username to the http user-agent header (default: None)
```

Sample usage and output:
```
> python fens2ccdb.py ../python-chinese-chess/fen > fens_eval.txt
Loaded 1000 FENs ...
Started parsing the FENs with concurrency 16 ...
Done. Scored 1000 FENs in 18.4s.
The file ../python-chinese-chess/fen contained 3 new chessdb.cn positions.
Rerunning the script after a short break should provide their evals.

> date
Sun 10 Sep 21:45:47 CEST 2023
```

---
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
