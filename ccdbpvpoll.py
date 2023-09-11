"""
   Script to monitor a position's PV on Chinese chessdb.cn at regular intervals.
"""
import argparse, asyncio, time, ccdblib
from datetime import datetime


async def main():
    parser = argparse.ArgumentParser(
        description="Monitor dynamic changes in a position's PV on Chinese chessdb.cn by polling it at regular intervals.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--epd",
        help="FEN/EPD of the position to monitor",
        default="rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w",
    )
    parser.add_argument(
        "--stable", action="store_true", help='pass "&stable=1" option to API'
    )
    parser.add_argument(
        "--sleep",
        type=int,
        default=3600,
        help="time interval between polling requests in seconds",
    )
    parser.add_argument(
        "-u",
        "--user",
        help="username for the http user-agent header",
    )
    args = parser.parse_args()

    ccdb = ccdblib.ccdbAPI(concurrency=1, user=args.user)
    q = await ccdb.queryscore(args.epd)
    s = q.get("status")
    if s != "ok" and s != "unknown":
        print("  It is imposssible to obtain a valid PV for the given position.")
        quit()

    while True:
        r = await (
            ccdb.querypvstable(args.epd) if args.stable else ccdb.querypv(args.epd)
        )
        pv = ccdblib.json2pv(r)
        e = ccdblib.json2eval(r)
        if type(e) == int:
            e = f"{e:4d}cp"
        else:
            e = " " * max(0, 6 - len(e)) + e
        print(f"  {datetime.now().isoformat()}: {e} -- {pv}")
        print("", flush=True)
        if args.sleep == 0:
            break
        time.sleep(args.sleep)


if __name__ == "__main__":
    asyncio.run(main())
