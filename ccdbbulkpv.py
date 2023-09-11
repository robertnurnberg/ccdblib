import argparse, asyncio, sys, os, time, ccdblib

sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "python-chinese-chess"))
import cchess


class bulkpv:
    def __init__(self, filename, stable, concurrency, user):
        self.filename = filename
        self.stable = stable
        self.isPGN = filename.endswith(".pgn")
        self.concurrency = concurrency
        self.ccdb = ccdblib.ccdbAPI(concurrency, user)

    def reload(self):
        self.metalist = []
        if self.isPGN:
            # pgn support in cchess seems to be rudimentary for now:
            # just one game per .pgn and we only get the final board
            board = cchess.Board.from_pgn(self.filename)
            self.metalist.append(board)
            self.count = len(self.metalist)
            print(
                f"Read {self.count} (opening) lines from file {self.filename}.",
                file=sys.stderr,
            )
        else:
            comments = 0
            with open(self.filename) as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.metalist.append(line)
                        if line.startswith("#"):
                            comments += 1
            self.count = len(self.metalist) - comments
            print(
                f"Read {self.count} FENs from file {self.filename}.",
                file=sys.stderr,
            )

    async def parse_all(self, batchSize=None):
        print(
            f"Started parsing the positions with concurrency {self.concurrency}"
            + (" ..." if batchSize == None else f" and batch size {batchSize} ..."),
            file=sys.stderr,
        )
        if batchSize is None:
            batchSize = len(self.metalist)
        self.tic = time.time()
        for i in range(0, len(self.metalist), batchSize):
            tasks = []
            for line in self.metalist[i : i + batchSize]:
                tasks.append(asyncio.create_task(self.parse_single_line(line)))

            for parse_line in tasks:
                print(await parse_line)

        elapsed = time.time() - self.tic
        print(
            f"Done. Polled {self.count} positions in {elapsed:.1f}s.",
            file=sys.stderr,
        )

    async def parse_single_line(self, line):
        if self.isPGN:
            epd = line.epd()
        else:
            if line.startswith("#"):  # ignore comments
                return line
            epd = " ".join(line.split()[:4])  # ccdb ignores move counters anyway
        r = await (
            self.ccdb.querypvstable(epd) if self.stable else self.ccdb.querypv(epd)
        )
        score = ccdblib.json2eval(r)
        pv = ccdblib.json2pv(r)
        if self.isPGN:
            line = epd
        return f"{line}{';' if line[-1] != ';' else ''} ccdb eval: {score}; PV: {pv}"


async def main():
    parser = argparse.ArgumentParser(
        description="A script that queries Chinese chessdb.cn for the PV of all positions in a file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "filename", help="PGN file if suffix is .pgn, o/w a text file with FENs"
    )
    parser.add_argument(
        "--stable", action="store_true", help='pass "&stable=1" option to API'
    )
    parser.add_argument(
        "-c",
        "--concurrency",
        help="Maximum concurrency of requests to ccdb.",
        type=int,
        default=16,
    )
    parser.add_argument(
        "-b",
        "--batchSize",
        help="Number of positions processed in parallel. Small values guarantee more responsive output, large values give faster turnaround.",
        type=int,
        default=None,
    )
    parser.add_argument(
        "-u",
        "--user",
        help="Add this username to the http user-agent header",
    )
    parser.add_argument(
        "--forever",
        action="store_true",
        help="Run the script in an infinite loop.",
    )
    args = parser.parse_args()
    bpv = bulkpv(args.filename, args.stable, args.concurrency, args.user)
    while True:  # if args.forever is true, run indefinitely; o/w stop after one run
        # re-reading the data in each loop allows updates to it in the background
        bpv.reload()
        await bpv.parse_all(args.batchSize)

        if not args.forever:
            break


if __name__ == "__main__":
    asyncio.run(main())
