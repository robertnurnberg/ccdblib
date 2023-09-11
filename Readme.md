# Library with wrapper functions for the Chinese chessdb.cn API

The library `ccdblib.py` allows to conveniently use the API of the Chinese Chess Cloud Database [chessdb.cn](https://chessdb.cn/query_en/) (ccdb), the largest online database of Chinese chess positions and openings, from within Python.

## This repo is work in progress ...

## Purpose

Provide a simple library with wrapper functions for the API of ccdb. All the wrapper functions will continuously query ccdb until a satisfactory response has been received.

## Usage

By way of example, three small application scripts are provided.

* [`fens2ccdb`](#fens2ccdb) - request evaluations from ccdb for FENs stored in a file
* [`ccdbpvpoll`](#ccdbpvpoll) - monitor a position's PV on ccdb over time
* [`cdbbulkpv`](#cdbbulkpv) - bulk-request PVs from ccdb for positions stored in a file

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

  2023-09-11T14:12:26.582862:    2cp -- c3c4 b7c7 h2e2 c9e7 b0a2 i9i8 e2e6 d9e8 h0g2 b9d8 e6e4 a9b9 a0b0 i8f8 i0h0 f8f5 c0e2 h9i7 a3a4 b9b3 h0h1 f5d5 i3i4 d8e6 b2c2 b3b0 a2b0 c6c5 c4c5 e6c5 h1b1 c7c2 b1b9 d5d9 b9d9 e9d9 b0c2 c5e4 e3e4 h7h4 e4e5 i7g8 d0e1 g8h6 c2b4 h4a4 b4a6 a4e4 a6b8 d9e9 e0d0 h6i4 g3g4 g6g5 g2i3 e4e3 g4g5 i4g5 i3g4 e3d3 e5f5 g5h7 g4h6 d3d6 b8c6 h7f6 f5f6
```

### `cdbbulkpv`

A command line program to bulk-request from ccdb the PVs of all the positions stored in a file.

```
usage: ccdbbulkpv.py [-h] [--stable] [-c CONCURRENCY] [-b BATCHSIZE] [-u USER] [--forever] filename

A script that queries Chinese chessdb.cn for the PV of all positions in a file.

positional arguments:
  filename              PGN file if suffix is .pgn, o/w a text file with FENs

options:
  -h, --help            show this help message and exit
  --stable              pass "&stable=1" option to API (default: False)
  -c CONCURRENCY, --concurrency CONCURRENCY
                        Maximum concurrency of requests to ccdb. (default: 16)
  -b BATCHSIZE, --batchSize BATCHSIZE
                        Number of positions processed in parallel. Small values guarantee more responsive output, large values give faster turnaround. (default: None)
  -u USER, --user USER  Add this username to the http user-agent header (default: None)
  --forever             Run the script in an infinite loop. (default: False)
```

Sample usage and output:
```
> python ccdbbulkpv.py ../python-chinese-chess/fen > fens_pv.txt
Read 1000 FENs from file ../python-chinese-chess/fen.
Started parsing the positions with concurrency 16 ...
Done. Polled 1000 positions in 19.5s.
```

---
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
