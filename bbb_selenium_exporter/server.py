import os
import signal
import sys
import time
from argparse import ArgumentParser
from collections import namedtuple
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread, Timer, Lock
from urllib.parse import parse_qs, urlparse

from mpipe import UnorderedStage, Pipeline
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from .collect import collect


Target = namedtuple('Target', ['host', 'secret']) 


class Repeater(Timer):
    def run(self):
        self.function(*self.args, **self.kwargs)
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


class Scheduler():
    def __init__(self, runner):
        self.runner = runner
        self.targets = dict()

    def add(self, target):
        timer = Repeater(self.interval, lambda: self.runner.put(target))
        self.targets[target] = timer
        timer.start()

    def remove(self, target):
        try:
            self.targets[target].cancel()
            del self.targets[target]
        except KeyError:
            pass

    def cancel_all(self):
        for target, timer in self.targets.items():
            timer.cancel()
            del self.targets[target]

    @staticmethod
    def factory(interval):
        return type('Scheduler', (Scheduler, object), {'interval': interval})


class ExecutionCache():
    def __init__(self, function, jobs, SchedulerClass):
        self._results = dict()
        self._targets = set()
        self._update_lock = Lock()

        self._runner = Pipeline(UnorderedStage(function, jobs))

        def fetch():
            for target, result in self._runner.results():
                if target in self._targets:
                    self._results[target.host] = result
                else:
                    print(f'dropping obsolete result for {target}')
        
        self._fetcher = Thread(target=fetch)
        self._fetcher.start()
        self.scheduler = SchedulerClass(self._runner)

    def teardown(self):
        self.scheduler.cancel_all()
        self._runner.put(None)
        self._fetcher.join()

    def update_targets(self, targets):
        with self._update_lock:
            new_targets = set(targets)
            old_targets = self._targets

            new_hosts = { target.host for target in targets }
            old_hosts = { target.host for target in self._targets }
            removed_hosts = old_hosts - new_hosts

            self._targets = new_targets
            
            for target in old_targets - new_targets:
                self.scheduler.remove(target)

                if target.host in removed_hosts:
                    try:
                        del self._results[target.host]
                    except KeyError:
                        pass

            for target in new_targets - old_targets:
                self.scheduler.add(target)


    def __getitem__(self, key):
        return self._results[key]


class CacheHandler(BaseHTTPRequestHandler):
    @staticmethod
    def factory(cache):
        return type('CacheHandler', (CacheHandler, object), {"cache": cache})

    def do_GET(self):
        if not self.path.startswith('/metrics'):
            self.send_error(404)
            return

        try:
            target = parse_qs(urlparse(self.path).query)['target'][0]
        except KeyError:
            self.send_error(400, 'query parameter "target" is missing')
            return

        try:
            result = self.cache[target]
        except KeyError:
            self.send_error(404, 'unknown target')
            return

        self.send_response(200)
        self.send_header('Content-Type', CONTENT_TYPE_LATEST)
        self.end_headers()
        self.wfile.write(result)

def prepare_selenium_test(headless):
    def run_selenium_test(target):
        return target, generate_latest(collect(target.host, target.secret, headless=headless))
    return run_selenium_test


def read_config(path):
    with open(path, 'r') as config_file:
        lines = config_file.readlines()

    targets = dict()
    for linenum, line in enumerate(lines):
        host, _, secret = line.strip().partition(' ')
        if not secret or host.startswith('#'):
            continue
        if host in targets:
            print(f'duplicate host {host} configured in line {linenum+1}, ignoring')
            continue
        targets[host] = Target(host, secret)

    return targets.values()


def main():
    ap = ArgumentParser(prog='bbb-selenium-exporter')
    ap.add_argument('--bind', '-b', help='bind to address:port', default='localhost:9123')
    ap.add_argument('--config', '-c', help='config file with BBB instances to scrape', default='/etc/bbb-selenium-exporter/targets')
    ap.add_argument('--interval', '-i', help='interval between scrapes of the same host in seconds', type=int, default=900)
    ap.add_argument('--jobs', '-j', help='number of parallel webdriver instances', type=int, default=len(os.sched_getaffinity(0)))
    ap.add_argument('--gui', help='disable headless mode for webdriver', action='store_true')
    args = ap.parse_args()

    cache = ExecutionCache(prepare_selenium_test(not args.gui), args.jobs, Scheduler.factory(args.interval))

    bindhost, _, bindport = args.bind.rpartition(":")
    Thread(target=lambda: HTTPServer((bindhost, int(bindport)), CacheHandler.factory(cache)).serve_forever(), daemon=True).start()

    def reload_targets(*_):
        cache.update_targets(read_config(args.config))

    reload_targets()

    def shutdown(*_):
        print('got SIGTERM, shutting down')
        cache.teardown()
        print("cache teardown done")
        sys.exit(0)

    signal.signal(signal.SIGHUP, reload_targets)
    signal.signal(signal.SIGTERM, shutdown)

    while True:
        time.sleep(1)
