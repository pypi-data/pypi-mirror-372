import logging
import time
from collections import namedtuple

from zeroconf import IPVersion
from zeroconf import ServiceBrowser
from zeroconf import Zeroconf

log = logging.getLogger(__name__)

MokuInfo = namedtuple(
    "MokuInfo",
    [
        "name",
        "netver",
        "fwver",
        "hwver",
        "serial",
        "colour",
        "bootmode",
        "ipv4_addr",
        "ipv6_addr",
    ],
)


class Finder(object):
    def __init__(self, on_add=None, on_remove=None):
        self.moku_list = []
        self.finished = False
        self.filter = None
        self.timeout = 5
        self.zero_conf = Zeroconf(ip_version=IPVersion.V4Only)
        self.browser = None
        self.on_add = on_add
        self.on_remove = on_remove

    @staticmethod
    def _get_parsed_addresses(info):
        ipv4 = info.parsed_addresses()[0]
        # TODO
        ipv6 = ""
        return [ipv4, ipv6]

    def _parse_05(self, info):
        name = info.name.split("." + info.type)[0]
        p = info.properties
        addresses = self._get_parsed_addresses(info)
        return MokuInfo(
            name=name,
            netver=int(p[b"netver"]),
            fwver=int(p[b"fwver"]),
            hwver=float(p[b"hwver"]),
            serial=int(p[b"serial"]),
            colour=(p.get(b"colour", p.get(b"color")) or b"").decode("utf8"),
            bootmode=p[b"bootmode"].decode("utf8"),
            ipv4_addr=addresses[0],
            ipv6_addr=addresses[1],
        )

    def _parse_04(self, info):
        name = info.name.split("." + info.type)[0]
        p = info.properties
        addresses = self._get_parsed_addresses(info)
        return MokuInfo(
            name=name,
            netver=int(p[b"netver"]),
            fwver=int(p[b"device.fw_version"]),
            hwver=float(p[b"device.hw_version"]),
            serial=int(p[b"device.serial"]),
            colour=p[b"device.colour"].decode("utf8"),
            bootmode=p[b"system.bootmode"].decode("utf8"),
            ipv4_addr=addresses[0],
            ipv6_addr=addresses[1],
        )

    def _parse_02(self, info):
        name = info.name.split("." + info.type)[0]
        p = info.properties
        addresses = self._get_parsed_addresses(info)
        return MokuInfo(
            name=name,
            netver=int(p[b"netver"]),
            fwver=int(p[b"system.micro"]),
            hwver=float(p[b"device.hw_version"]),
            serial=int(p[b"device.serial"]),
            colour=p[b"device.colour"].decode("utf8"),
            bootmode=p[b"system.bootmode"].decode("utf8"),
            ipv4_addr=addresses[0],
            ipv6_addr=addresses[1],
        )

    def add_service(self, zeroconf, service_type, name):
        info = zeroconf.get_service_info(service_type, name)
        if info is None:
            return

        try:
            parsers = {0.2: self._parse_02, 0.4: self._parse_04, 0.5: self._parse_05}
            record = parsers[float(info.properties[b"txtver"])](info)
        except Exception as e:
            log.error(e)
            return

        if self.filter is None or self.filter(record):
            self.moku_list.append(record)

            if self.on_add:
                self.on_add(name, record)

    def remove_service(self, zeroconf, service_type, name):
        if self.on_remove:
            self.on_remove(name)

    def update_service(self, zeroconf, service_type, name):
        pass

    def start(self):
        self.browser = ServiceBrowser(
            self.zero_conf, "_moku._tcp.local.", listener=self
        )

    def close(self):
        self.zero_conf.close()

    def find_all(self, timeout=5, filter=None):
        self.timeout = timeout
        self.filter = filter
        self.start()
        start = time.time()
        try:
            while (
                time.time() - start < timeout
                and not self.browser.done
                and (not self.finished)
            ):
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.zero_conf.close()
        return self.moku_list
