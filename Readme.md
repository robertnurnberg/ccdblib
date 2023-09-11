# Library with wrapper functions for the Chinese chessdb.cn API

The library `ccdblib.py` allows to conveniently use the API of the Chinese Chess Cloud Database [chessdb.cn](https://chessdb.cn/query_en/) (ccdb), the largest online database of Chinese chess positions and openings, from within Python.

## This repo is work in progress ...

## Purpose

Provide a simple library with wrapper functions for the API of ccdb. All the wrapper functions will continuously query ccdb until a satisfactory response has been received.

## Usage

By way of example, two small application scripts are provided.

* [`fens2ccdb`](#fens2ccdb) - request evaluations from ccdb for FENs stored in a file
* [`ccdbpvpoll`](#ccdbpvpoll) - monitor a position's PV on ccdb over time

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
                        Maximum concurrency of requests to ccdb. (default: 16)
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


### `ccdbpvpoll`

A command line program to monitor dynamic changes in a position's PV on ccdb.

```
usage: ccdbpvpoll.py [-h] [--epd EPD] [--stable] [-sleep SLEEP] [-u USER]

Monitor dynamic changes in a position's PV on Chinese chessdb.cn by polling it at regular intervals.

options:
  -h, --help            show this help message and exit
  --epd EPD             FEN/EPD of the position to monitor (default: rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w)
  --stable              pass "&stable=1" option to API (default: False)
  --sleep SLEEP         time interval between polling requests in seconds (default: 3600)
  -u USER, --user USER  username for the http user-agent header (default: None)
```

Sample usage and output:
```
> python ccdbpvpoll.py
  2023-09-11T13:12:25.923307:    2cp -- c3c4 b7c7 h2e2 c9e7 b0a2 i9i8 e2e6 d9e8 h0g2 b9d8 e6e5 i8f8 g3g4 g6g5 g4g5 f8g8 c0e2 g8g5 e3e4 h9g7 g2e3 h7h5 e3g4 h5e5 e4e5 c7c4 d0e1 c4e4 b2b4 a9b9 a0b0 e4f4 i0i1 g7h5 i1f1 g5e5 g4h6 f4d4 f1f3 c6c5 a3a4 e5d5 b4b8 d5d6 h6f5 d6d7 f3b3 h5f4 b3f3 f4h5

```

---
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
