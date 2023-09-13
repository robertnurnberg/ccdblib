"""
   Wrapper functions to access Chinese chessdb.cn from within Python.
   See API documentation at https://www.chessdb.cn/cloudbook_api_en.html
"""
import asyncio, requests, sys, time, threading, concurrent.futures
from datetime import datetime


class AtomicInteger:
    def __init__(self, value=0):
        self._value = int(value)
        self._lock = threading.Lock()

    def inc(self, d=1):
        with self._lock:
            self._value += int(d)
            return self._value

    def dec(self, d=1):
        return self.inc(-d)

    def get(self):
        with self._lock:
            return self._value

    def set(self, v):
        with self._lock:
            self._value = int(v)
            return self._value


class AtomicDict:
    def __init__(self):
        self._lock = threading.Lock()
        self._cache = {}

    def get(self, key):
        with self._lock:
            return self._cache.get(key)

    def set(self, key, value):
        with self._lock:
            self._cache[key] = value


def ban2action(ban):
    return "&ban=move:" + "|".join(f"move:{move}" for move in ban) if ban else ""


class ccdbAPI:
    def __init__(self, concurrency, user=None):
        # use a session to keep alive the connection to the server
        self.session = requests.Session()
        self.user = "" if user is None else str(user)
        # a semaphore to limit the number of concurrent accesses to the API
        self.semaphoreAPI = asyncio.Semaphore(concurrency)
        # a thread pool to do some of the blocking IO
        self.executorWork = concurrent.futures.ThreadPoolExecutor(
            max_workers=concurrency
        )

    def __apicall(self, url, timeout):
        try:
            response = self.session.get(
                url,
                timeout=timeout,
                headers={"user-agent": "ccdblib" + bool(self.user) * "/" + self.user},
            )
            response.raise_for_status()
            content = response.json()
        except Exception:
            content = None
        return content

    async def __ccdbapicall(self, action, timeout=15):
        """co-routine to access the API"""
        async with self.semaphoreAPI:
            return await asyncio.get_running_loop().run_in_executor(
                self.executorWork,
                self.__apicall,
                "http://www.chessdb.cn/chessdb.php" + action,
                timeout,
            )

    async def generic_call(self, action, fen, optionString=""):
        # action can be: "queryall", "querybest", "query", "querysearch", "queryscore", "querypv", "queryrule", "queue"
        # returns dict from API call to chessdb.cn with "status" guaranteed to be one of: "ok", "checkmate", "stalemate", "unknown", "nobestmove", "invalid board", "invalid movelist"
        timeout = 5
        success = False
        first = True
        lasterror = ""

        while not success:
            # sleep a bit before further requests
            if not first:
                # increase timeout after every attempt, up to a maximum
                if timeout < 60:
                    timeout = min(timeout * 1.5, 60)
                else:
                    print(
                        datetime.now().isoformat(),
                        " - failed to get reply for : ",
                        fen,
                        " last error: ",
                        lasterror,
                        file=sys.stderr,
                        flush=True,
                    )
                await asyncio.sleep(timeout)
            else:
                first = False

            content = await self.__ccdbapicall(
                f"?action={action}&board={fen}{optionString}&json=1", timeout
            )

            if content is None:
                lasterror = f"Something went wrong with {action}{optionString}"
                continue

            elif action == "queue" and content == {}:
                # empty dict is returned for mates and stalemates
                content = {"status": "ok"}
                lasterror = "Enqueued position"
                success = True

            elif action == "queryrule" and content == {}:
                # empty dict is returned for missing movelist
                content = {"status": "invalid movelist"}
                lasterror = "Invalid movelist"
                success = True

            elif "status" not in content:
                lasterror = "Malformed reply, not containing status"
                continue

            elif content["status"] == "invalid board":
                # nothing to be done, bail out and return to caller
                lasterror = "Invalid board"
                success = True

            elif content["status"] == "invalid movelist":
                # nothing to be done, bail out and return to caller
                lasterror = "Invalid movelist"
                success = True

            elif content["status"] == "rate limit exceeded":
                lasterror = "Rate limit exceeded"
                continue

            elif content["status"] == "unknown":
                lasterror = "Queried an unknown position"
                success = True

            elif content["status"] == "nobestmove":
                lasterror = "Asked for a move in mate/stalemate/unknown position"
                success = True

            elif content["status"] == "ok":
                if (
                    (action == "queryall" and "moves" not in content)
                    or (action == "queryrule" and "moves" not in content)
                    or (
                        action == "querybest"
                        and "move" not in content
                        and "search_moves" not in content
                        and "egtb" not in content
                    )
                    or (
                        action == "query"
                        and "move" not in content
                        and "search_moves" not in content
                        and "egtb" not in content
                    )
                    or (
                        action == "querysearch"
                        and "search_moves" not in content
                        and "egtb" not in content
                    )
                    or (action == "queryscore" and "eval" not in content)
                    or (
                        action == "querypv"
                        and (
                            "score" not in content
                            or "depth" not in content
                            or "pv" not in content
                        )
                    )
                ):
                    lasterror = "Unexpectedly missing keys"
                    continue
                else:
                    success = True

            elif content["status"] == "checkmate" or content["status"] == "stalemate":
                success = True

            else:
                lasterror = f"Surprise reply with status = {content['status']}"
                continue

        content["fen"] = fen  # add "fen" key to dict, used e.g. for PV SAN
        return content

    async def queryall(self, fen, ban=[]):
        # returns dict with keys "status", "moves" and "ply" where "moves" is a sorted list of dict's with keys "uci", "score", "rank", "note" and "winrate" (sorted by eval and rank)
        # goes 1 ply along scored moves, gets eval of these children, makes that the (updated) scores of the scored moves and reports these
        return await self.generic_call("queryall", fen, ban2action(ban))

    async def showall(self, fen, ban=[]):
        # same as queryall, but returns _all_ possible moves, with "??" for score of unscored moves
        return await self.generic_call("queryall", fen, ban2action(ban) + "&showall=1")

    async def querybest(self, fen, ban=[]):
        # returns one of the rank == 2 moves in a dict with keys "status" and either "move", "search_moves or "egtb"
        # also triggers automatic back-propagation on ccdb
        return await self.generic_call("querybest", fen, ban2action(ban))

    async def query(self, fen, ban=[]):
        # returns one of the rank > 0 moves in a dict with keys "status" and either "move", "search_moves or "egtb"
        # also triggers automatic back-propagation on ccdb
        return await self.generic_call("query", fen, ban2action(ban))

    async def querysearch(self, fen, ban=[]):
        # returns all of the rank > 0 moves in a dict with keys "status" and either "search_moves" or "egtb"
        return await self.generic_call("querysearch", fen, ban2action(ban))

    async def queryscore(self, fen, ban=[]):
        # returns dict with keys "status", "eval", "ply"
        return await self.generic_call("queryscore", fen, ban2action(ban))

    async def querypv(self, fen, ban=[]):
        # returns dict with keys "status", "score", "depth", "pv"
        # also triggers automatic back-propagation on ccdb
        return await self.generic_call("querypv", fen, ban2action(ban))

    async def querypvstable(self, fen, ban=[]):
        # same as querypv, but returns _stable_ PV (always GUI's top move)
        return await self.generic_call("querypv", fen, ban2action(ban) + "&stable=1")

    async def queryrule(self, fen, movelist, reptimes=1):
        # pass movelist as list of uci strings
        return await self.generic_call(
            "queryrule", fen, f"&movelist={'|'.join(movelist)}&reptimes={reptimes}"
        )

    async def queue(self, fen):
        # returns dict with key "status"
        # schedules position for analysis, scoring at least 5 moves, and does some recursion
        # also triggers automatic back-propagation on ccdb
        return await self.generic_call("queue", fen)


def json2eval(r):
    # turns a json response from the API into an evaluation, if possible
    # output: on success eval/score E as reported by ccdb, otherwise "mated", "invalid" or ""
    # E is either "??" or an integer E. in the latter case 30000-ply = mate in ply
    if r is None:  # only needed for buggy json responses from ccdb
        return "invalid json reply"
    if "status" not in r:
        return ""
    if r["status"] == "checkmate":
        return "mated"
    if r["status"] == "stalemate":
        return 0
    if r["status"] == "invalid board":
        return "invalid"
    s = ""
    if "moves" in r and "score" in r["moves"][0]:
        s = r["moves"][0]["score"]
    elif "eval" in r:
        s = r["eval"]
    elif "score" in r:
        s = r["score"]
    if type(s) == int and abs(s) > 10000:
        ply = 30000 - abs(s)
        s = "" if s > 0 else "-"
        s += f"M{ply}"
    if s == "??":
        s = ""
    return s


def json2pv(r, ply=None):
    # turns the PV from a json response from the API into a string
    # output: PV as a string, if possible, otherwise ""
    if r is None:  # only needed for buggy json responses from ccdb
        return "invalid json reply"
    if "status" not in r:
        return ""
    if "pv" not in r:
        return ""
    s = " ".join(tuple(r["pv"]))
    return s
