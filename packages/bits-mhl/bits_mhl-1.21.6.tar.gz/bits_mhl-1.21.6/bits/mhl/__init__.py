"""Initialize the bits.mhl module."""

import re

import netaddr

from bits.mhl.types import AvailableIp, CnameRecord, Comment, Host, MxRecord, NsRecord, ReservedIp

# define the field names of the mhl columns in order
FIELDNAMES = [
    'target',       # IP or CNAME/MX/NS Target
    'username',     # Username (Owner)
    'mac',          # MAC Address (or MX Priority)
    'hostnames',    # Hostnames (comma-separated)
    'ttl',          # TTL
    'hosttype',     # Host Type
    'location',     # Location code (see LOCATIONS below)
    'tags',         # Tags for runaround, icinga, etc.
    'comments',     # Comments
]

# define a list of valid host types
HOSTTYPES = [
    'chrome',       # Chrome OS Desktop or Laptop
    'cname',        # Special type for DNS CNAME records
    'device',       # Generic host without DHCP
    'dhcpdevice',   # Generic host with DHCP
    'external',     # External (non-Broad) host (Amazon, Google, etc.)
    'ip_alias',     # Additional IP Alias on Host (same MAC as host)
    'mac_svr',      # Mac OS X Server
    'mac',          # Mac OS X Desktop or Laptop
    'mx',           # Special type for DNS MX records
    'netapp',       # NetApp Filers
    'ns',           # Special type for DNS NS records
    'pc',           # Windows or Linux Desktop or Laptop
    'printer',      # Printer
    'round_robin',  # Special type to handle hosts with Round Robin DNS
    'unix_svr',     # Unix Server
    'win_svr',      # Windows Desktop or Laptop
]

# define a list of valid locations
LOCATIONS = [
    'a',  # 75 Ames Street
    'b',  # 105 Broadway
    'c',  # 320 Charles Street
    'e',  # 190 Fifth Street (decommissioned)
    'g',  # 415 Main Street / 7 Cambridge Center
    'i',  # 50 Inner Belt
    'l',  # LIMS Network
    'm',  # Markley Lowell
    'r',  # Remote site (ex. Oxford Street)
    's',  # 1 Summer Street
    'v',  # 5 Cambridge Center (decommissioned)
    'w',  # Broad Internal Wifi
    'x',  # Museum
]

# define a list of non-people owners of hosts
SPECIAL_OWNERS = [
    'BITS Computer',
    'Classroom Computer',
    'Conference Room Computer',
    'Hotel Computer',
    'Loaner Computer',
]

#
# Network Ranges
#

# define the broad network ip ranges
BROAD_HOSTS = netaddr.IPSet([
    # loopback
    netaddr.IPNetwork('127.0.0.1/32'),

    # internal ranges
    netaddr.IPNetwork('10.0.0.0/8'),
    netaddr.IPNetwork('172.16.0.0/12'),
    netaddr.IPNetwork('192.168.0.0/16'),

    # public range
    netaddr.IPNetwork('69.173.64.0/18'),

    # networking points
    netaddr.IPAddress('207.210.142.158'),   # nox cps interface
    netaddr.IPAddress('207.210.143.158'),   # nox r&e interface
    netaddr.IPAddress('216.55.4.6'),        # xo interface
    netaddr.IPAddress('209.143.142.65'),   # 11:11 fiori
    netaddr.IPAddress('209.143.142.66'),   # 11:11 fiori-qa
    netaddr.IPAddress('209.143.142.67'),   # 11:11 fiori-dev
])

# regular hosts
REGULAR_HOSTS = netaddr.IPSet([
    netaddr.IPNetwork('10.1.0.0/19'),
    netaddr.IPNetwork('10.1.128.0/24'),
    netaddr.IPNetwork('10.75.0.0/20'),
    netaddr.IPNetwork('10.75.100.0/22'),
    netaddr.IPNetwork('10.75.104.0/22'),
    netaddr.IPNetwork('10.75.108.0/22'),
    netaddr.IPNetwork('10.75.112.0/22'),
    netaddr.IPNetwork('10.75.116.0/23'),
    netaddr.IPNetwork('10.75.16.0/21'),
    netaddr.IPNetwork('172.18.12.0/24'),
    netaddr.IPNetwork('18.103.12.0/22'),
    netaddr.IPNetwork('18.103.16.0/21'),
    netaddr.IPNetwork('18.103.2.0/23'),
    netaddr.IPNetwork('18.103.24.0/22'),
    netaddr.IPNetwork('69.173.104.0/22'),
    netaddr.IPNetwork('69.173.108.0/22'),
    netaddr.IPNetwork('69.173.114.0/24'),
    netaddr.IPNetwork('69.173.115.0/24'),
    netaddr.IPNetwork('69.173.120.0/22'),
    netaddr.IPNetwork('69.173.96.0/21'),
])
REGULAR_HOSTS.add(netaddr.IPRange('192.168.141.150', '192.168.141.255'))

# cellario network hosts
CELLARIO_HOSTS = netaddr.IPNetwork('192.168.10.0/23')

# lab network hosts
LAB_HOSTS = netaddr.IPSet([
    netaddr.IPNetwork('192.168.1.0/24'),
    netaddr.IPNetwork('192.168.2.0/23'),
    netaddr.IPNetwork('192.168.8.0/23'),
    netaddr.IPNetwork('192.168.96.0/21'),

    netaddr.IPNetwork('192.168.212.0/24'),
])
LAB_HOSTS.add(netaddr.IPRange('192.168.141.0', '192.168.141.150'))
LAB_HOSTS.add(netaddr.IPRange('192.168.200.20', '192.168.200.127'))

# qa network hosts
QA_HOSTS = netaddr.IPNetwork('192.168.105.0/24')

# restricted network hosts
RESTRICTED_HOSTS = netaddr.IPNetwork('192.168.60.0/24')


class MHL:
    """MHL class."""

    def __init__(
        self,
        path='/sysman/install/broad/master.host.listing',
        lockfile='/sysman/install/broad/locks/master.host.listing.lock',
        people=None,
        verbose=False
    ):
        """Initialize the object."""
        self.path = path
        self.lockfile = lockfile
        self.verbose = verbose
        self.mhlfile = MHLFile(path, lockfile, people, verbose=self.verbose)


class MHLFile:
    """MHL class."""

    def __init__(self, path, lockfile, people=None, verbose=False):
        """Initialize the object."""
        self.path = path
        self.people = people
        self.lockfile = lockfile
        self.verbose = verbose

        # get the lines of the mhl as objects
        self.lines = self.get_lines()
        self.linecount = len(self.lines)

        # records
        self.cnames = {}
        self.hosts = {}
        self.mxs = {}
        self.nss = {}
        self.records = {}

        # tracking duplicates
        self.hostnames = {}
        self.ips = {}
        self.macs = {}

        # get records
        self.get_records()

        # round robins
        self.round_robins = self.get_round_robins()

        # statistics
        self.hosttypes = self.get_hosttypes()
        self.kinds = self.get_kinds()
        self.record_types = self.get_record_types()
        self.types = self.get_types()

        # check for errors, warnings, duplicates and out-of-order issues
        self.check_lines()
        self.check_duplicates()
        self.check_order()

        # if we have people data, let's add emplids to all our host records
        self.insert_emplids(people)

        # errors and warnings
        self.errors = self.get_errors()
        self.warnings = self.get_warnings()

        # find missing IP addresses
        self.missing_ips = self.get_missing_ips()

    def check_duplicate_available_ips(self):
        """Check available IPs for duplicates."""
        for line in self.lines:
            if line.kind != 'available_ip':
                continue
            entry = line.entry
            if entry.ip not in self.ips:
                self.ips[entry.ip] = line
            else:
                warning = f"Duplicate Available IP Address: {entry.ip}"
                line.warnings.append(warning)

    def check_duplicate_hosts(self, kind='entry'):  # noqa: PLR0912
        """Check host entries for duplicates."""
        # now check host lines for duplicates
        for line in self.lines:
            if line.kind != kind:
                continue

            entry = line.entry
            hostname = entry.hostname

            # only look at host entries
            if entry.type != 'host':
                continue

            if line.is_failover:
                continue

            # check hostname
            if hostname not in self.hostnames:
                self.hostnames[hostname] = line
            else:
                error = f"Duplicate Hostname: {hostname}"
                line.errors.append(error)

            # check cnames
            cnames = entry.cnames
            for cname in cnames:
                if cname not in self.hostnames:
                    self.hostnames[cname] = line
                else:
                    error = f"Duplicate Hostname: {cname}"
                    line.errors.append(error)

            # check ip address
            if entry.ip and entry.ip != '-':
                if entry.ip not in self.ips:
                    self.ips[entry.ip] = line
                else:
                    error = f"Duplicate IP Address: {entry.ip}"
                    line.errors.append(error)

            # check mac address
            if entry.hosttype not in ['ip_alias']:
                mac = entry.mac
                if mac and mac != '-':
                    if mac not in self.macs:
                        self.macs[mac] = line
                    else:
                        error = f"Duplicate MAC Address: {mac}"
                        line.errors.append(error)

    def check_duplicate_reserved_ips(self):
        """Check reserved IPs for duplicates."""
        for line in self.lines:
            if line.kind != 'reserved_ip':
                continue
            entry = line.entry
            if entry.ip not in self.ips:
                self.ips[entry.ip] = line
            else:
                warning = f"Duplicate Reserved IP Address: {entry.ip}"
                line.warnings.append(warning)

    def check_duplicates(self):
        """Check entries for duplicates."""
        # add round robins first
        for hostname, data in self.round_robins.items():
            self.hostnames[hostname] = data

        # add cnames, mx records and ns record next
        for hostname, data in self.cnames.items():
            self.hostnames[hostname] = data
        for hostname, data in self.mxs.items():
            self.hostnames[hostname] = data
        for hostname, data in self.nss.items():
            self.hostnames[hostname] = data

        # check reserved IPs for duplicates
        self.check_duplicate_reserved_ips()

        # check host records for duplicates
        self.check_duplicate_hosts()

        # check disabled host records for duplicates
        self.check_duplicate_hosts(kind='disabled_entry')

        # check available IPs
        self.check_duplicate_available_ips()

    def check_lines(self):
        """Check the lines of the MHL files."""
        for line in self.lines:
            if not line or not line.entry:
                continue
            line.entry.check()

    def get_missing_ips(self):
        """Check the file for missing IP addresses."""
        missing_ips = []
        subnets = {}
        for line in self.lines:
            if not line.entry:
                continue
            if not line.entry.ip:
                continue
            subnet = '.'.join(line.entry.ip.split('.')[:3])
            cidr = netaddr.IPNetwork(f"{subnet}.0/24")
            if cidr not in subnets:
                subnets[cidr] = []
            subnets[cidr].append(netaddr.IPAddress(line.entry.ip))

        # check each subnet for missing ips
        for subnet in sorted(subnets):
            ips = sorted(subnets[subnet])

            # get the start and end ips from mhl
            first = ips[0]
            last = ips[-1]
            iprange = netaddr.IPSet(netaddr.IPRange(first, last))

            # get the used ips from the file
            usedips = netaddr.IPSet(ips)

            # find the ips that are missing from the file
            missing = iprange ^ usedips

            if not missing:
                continue

            missing_ips.extend(missing)

            # display missiong IP addresses
            if self.verbose:
                print(f"{subnet} missing IPs: {len(missing)}")

        return sorted(missing_ips)

    def display_errors(self):
        """Display errors."""
        errors = self.get_errors()
        if errors:
            print(f"\nERRORS [{len(errors)}]:")
            for line in errors:
                print(f"\n{line.linenum}: {line.line}")
                print("  - \n - ".join(line.errors))

    def display_warnings(self):
        """Display warnings."""
        warnings = self.get_warnings()
        if warnings:
            print(f"\nWarnings [{len(warnings)}]:")
            for line in warnings:
                print(f"\n{line.linenum}: {line.line}")
                print("  - \n - ".join(line.warnings))

    def get_errors(self):
        """Return a list of lines with errors."""
        errors = []
        for line in self.lines:
            if line.errors:
                errors.append(line)
        self.errors = errors
        return errors

    def get_hosttypes(self):
        """Return a dict of the entry hosttypes in the file."""
        hosttypes = {}
        for line in self.lines:
            if line.entry and line.entry.type == 'host':
                hosttype = line.entry.hosttype
                if hosttype in hosttypes:
                    hosttypes[hosttype] += 1
                else:
                    hosttypes[hosttype] = 1
        return hosttypes

    def get_kinds(self):
        """Return a dict of the kinds in the file."""
        kinds = {}
        for line in self.lines:
            if line.kind not in kinds:
                kinds[line.kind] = 1
            else:
                kinds[line.kind] += 1
        return kinds

    def get_lines(self):
        """Get the lines of the MHL in object form."""
        lines = []
        linenum = 0
        for line in self.readlines():
            linenum += 1
            out = MHLLine(line, linenum)
            lines.append(out)
        return lines

    def check_order(self):
        """Check order of IP addresses in the file."""
        # check for out of order IP addresses in the file
        last_ip = None

        for line in self.lines:
            # skip empty lines
            if not line:
                continue

            # skip non-entries or entries without an ip:
            if not line.entry or not line.entry.ip:
                continue

            # skip entries with an invalid ip address
            try:
                ipaddr = netaddr.IPAddress(line.entry.ip)
            except Exception as exc:
                print(f"%{line.line}\n\t{str(exc)}")
                continue

            # check the order of the ip addresses in the file
            if not last_ip:
                last_ip = ipaddr
            else:
                if last_ip > ipaddr:
                    error = f"IP Address out of order: {line.entry.ip}"
                    line.errors.append(error)
                last_ip = ipaddr

    def get_records(self):  # noqa: PLR0912
        """Assemble all lines into records."""
        # for each line that is an entry, determine what type it is
        # for mx and ns records, collapse same-named records into one record
        # with multiple targets
        for line in self.lines:
            if line.kind != 'entry':
                continue

            entry = line.entry
            hostname = entry.hostname
            # cname
            if entry.type == 'cname':
                if hostname not in self.cnames:
                    self.cnames[hostname] = entry
                else:
                    error = f"Duplicate CNAME: {hostname}"
                    line.errors.append(error)
            # mx
            elif entry.type == 'mx':
                if hostname not in self.mxs:
                    self.mxs[hostname] = entry
                else:
                    self.mxs[hostname].targets += entry.targets
            # ns
            elif entry.type == 'ns':
                if hostname not in self.nss:
                    self.nss[hostname] = entry
                else:
                    self.nss[hostname].targets += entry.targets
            # host
            elif entry.type == 'host':
                if hostname not in self.hosts:
                    self.hosts[hostname] = entry
                else:
                    error = f"Duplicate Host: {hostname}"
                    line.errors.append(error)

        # now that we've turned the entries into records, check for duplicates

        # cnames
        for hostname, data in self.cnames.items():
            if hostname not in self.records:
                self.records[hostname] = data
            else:
                error = f"Duplicate Record [CNAME]: {hostname}"
                line.errors.append(error)

        # mx records
        for hostname, data in self.mxs.items():
            if hostname not in self.records:
                self.records[hostname] = data
            else:
                error = f"Duplicate Record [MX]: {hostname}"
                line.errors.append(error)

        # ns records
        for hostname, data in self.nss.items():
            if hostname not in self.records:
                self.records[hostname] = data
            else:
                error = f"Duplicate Record [NS]: {hostname}"
                line.errors.append(error)

        # hosts
        for hostname, data in self.hosts.items():
            if hostname not in self.records:
                self.records[hostname] = data
            else:
                error = f"Duplicate Record [Host]: {hostname}"
                line.errors.append(error)

    def get_record_types(self):
        """Return a dict of the record types in the file."""
        record_types = {}
        for _, record in self.records.items():
            record_type = record.type
            if record_type in record_types:
                record_types[record_type] += 1
            else:
                record_types[record_type] = 1
        return record_types

    def get_round_robins(self):
        """Get round robin hosts."""
        round_robins = {}
        for _, host in self.hosts.items():
            if host.round_robin:
                round_robin = host.round_robin
                if round_robin in round_robins:
                    round_robins[round_robin].append(host)
                else:
                    round_robins[round_robin] = [host]
        return round_robins

    def get_types(self):
        """Return a dict of the entry types in the file."""
        types = {}
        for line in self.lines:
            if line.entry:
                hosttype = line.entry.type
                if hosttype in types:
                    types[hosttype] += 1
                else:
                    types[hosttype] = 1
        return types

    def get_warnings(self):
        """Return a list of lines with warnings."""
        warnings = []
        for line in self.lines:
            if line.warnings:
                warnings.append(line)
        self.warnings = warnings
        return warnings

    def insert_emplids(self, people):
        """Insert emplids into all Host records that have owners."""
        if not people:
            return
        # create username -> emplid map
        emplids = {}
        for username in people:
            emplids[username] = people[username]['emplid']
        # update all hosts
        for hostname, host in self.hosts.items():
            username = host.username.replace('-', '')
            if not username:
                continue
            if username in people:
                if host.owner:
                    host.owner.emplid = emplids[username]
                else:
                    print(f"Host owner not found: {hostname} [{username}]")

    def readlines(self):
        """Read in the lines of the MHL file."""
        with open(self.path, encoding="ascii") as mhlfile:
            return mhlfile.readlines()

    def update_file(self):
        """Update the production instance of the MHL file."""
        # RCS version
        # - if lockfile already exists, exit
        # - create a lockfile
        # - checkout the mhl file from RCS
        # - verify that file is now checked out by me and locked
        # - write out a new copy of the file to a temporary location
        # - compare the two files and provide a diff
        # - overwrite the real file with the new file
        # - verify the two files are now the same
        # - check the file into RCS
        # - verify the file has been checked into RCS
        # return success

        # GCS version
        # write file to a GCS bucket - magic happens

        # GIT version
        # clone a version of the mhl repo into a directory
        # replace the mhl with the new version
        # check the git diff
        # git commit the changes
        # git push the changes

    def writelines(self, filename):
        """Write out the MHL file to disk."""
        # write out a new copy of the mhl to disk
        with open(filename, "w", encoding="ascii") as outputfile:
            lines = []
            for line in self.lines:
                lines.append(f"{line.line}\n")
            outputfile.writelines(lines)

    def writemissing(self, filename):
        """Write out the MHL file to disk including missing IPs."""
        # write out a new copy of the mhl to disk
        with open(filename, "w", encoding="ascii") as outputfile:
            lines = []
            missing_ips = sorted(self.missing_ips)
            last_ip = None

            for line in self.lines:
                ipaddr = None
                if line.entry and line.entry.ip:
                    ipaddr = netaddr.IPAddress(line.entry.ip)

                if not last_ip:
                    last_ip = ipaddr

                while ipaddr and missing_ips and ipaddr > missing_ips[0]:
                    lines.append(f"#{missing_ips.pop(0)}\n")

                lines.append(f"{line.line}\n")
            outputfile.writelines(lines)


class MHLLine:
    """MHL Line class."""

    fieldnames = FIELDNAMES
    hosttypes = HOSTTYPES
    locations = LOCATIONS
    special_owners = SPECIAL_OWNERS

    # network ranges
    broad_hosts = BROAD_HOSTS
    cellario_hosts = CELLARIO_HOSTS
    lab_hosts = LAB_HOSTS
    qa_hosts = QA_HOSTS
    regular_hosts = REGULAR_HOSTS
    restricted_hosts = RESTRICTED_HOSTS

    def __init__(self, line, linenum):
        """Initialize the object."""
        self.line = line.strip()
        self.linenum = linenum
        self.fields = line.strip().split('|')

        # errors and warnings
        self.errors = []
        self.warnings = []

        # blanks and comments
        self.is_blank = False
        self.is_comment = False
        self.is_failover = False

        # check if line is blank
        if not line.strip():
            self.is_blank = True
        # check if line is a comment
        elif re.match('^#', line):
            self.is_comment = True

        # set kind
        self.kind = self.get_kind()

        # set entry
        self.entry = self.get_entry()

        # Check for failover status
        if self.is_comment:
            if "failover" in getattr(self.entry, "tags", []):
                self.is_failover = True

    def check_ip(self, ipaddr):
        """Check an IP address for validity."""
        errors = []
        try:
            netaddr.IPAddress(ipaddr)
            # check if this ip address is in one of our known ranges
            if ipaddr not in self.broad_hosts:
                error = f"Unknown Network: {ipaddr}"
                self.warnings.append(error)
        except netaddr.core.AddrFormatError:
            error = f"Invalid IP Address: {ipaddr}"
            errors.append(error)
        return errors

    def get_entry(self):  # noqa: PLR0911,PLR0912
        """Return an entry based on the current line."""
        # blank entries
        if self.kind == 'blank':
            return None

        # errors
        if self.kind == 'error':
            error = f"Incorrect Field Count: {len(self.fields)}"
            self.errors.append(error)
            return None

        # comments
        if self.is_comment:
            if self.kind == 'available_ip':
                return AvailableIp(self)
            if self.kind == 'disabled_entry':
                hosttype = self.to_json().get('hosttype')
                if hosttype == 'cname':
                    return CnameRecord(self, disabled=True)
                if hosttype == 'mx':
                    return MxRecord(self, disabled=True)
                if hosttype == 'ns':
                    return NsRecord(self, disabled=True)
                return Host(self, disabled=True)
            if self.kind == 'reserved_ip':
                return ReservedIp(self)
            return Comment(self)

        # entries
        if self.kind == 'entry':
            hosttype = self.to_json().get('hosttype')
            if hosttype == 'cname':
                return CnameRecord(self)
            if hosttype == 'mx':
                return MxRecord(self)
            if hosttype == 'ns':
                return NsRecord(self)
            return Host(self)

        return None

    def get_kind(self):  # noqa: PLR0911
        """Return the kind of the current line."""
        num_fields = 2
        # blank line
        if self.is_blank:
            return 'blank'

        # comments, disabled entries and reserved IPs
        if self.is_comment:
            if len(self.fields) == len(self.fieldnames):
                return 'disabled_entry'
            if len(self.fields) == num_fields:
                return 'reserved_ip'
            if re.match(r'^#([0-9]+)(\.[0-9]+){3}', self.line):
                return 'available_ip'
            return 'comment'

        # entries
        if len(self.fields) == len(self.fieldnames):
            return 'entry'

        return 'error'

    def to_json(self):
        """Return a json representation of an MHL line."""
        line = {}
        fields = list(self.fields)
        for key in self.fieldnames:
            if fields:
                line[key] = fields.pop(0)
        return line
