import re


class RunningConfigParser():
    """
    Parser for running-config files of ruckus switch stack using FastIron software
    """

    def __init__(self, file):
        """
        class constructor
        :param file: running-config file path
        """
        self.file = file
        self.__full_config = {}
        self.__system_info = self.parse_system_info()
        self.__vlans = self.parse_vlans()

    @property
    def get_vlans(self):
        """
        Vlan configuration parser, find vlan id, name and tagged and untagged ports.
        Creates a list containing vlan dictionaries. VLAN dictionaries have the following structure:
        {'vlan_id': id, 'vlan_name': name, 'tagged_ports': list of tagged ports, 'untagged_ports': list of untagged
        ports
        :return: list() of VLAN dictionaries dict()
        """
        return self.__vlans

    @property
    def get_system_info(self):
        """
        System infos parser, extract hostname, address, gateway and version
        :return: dict()
        """
        return self.__system_info

    def get_full_config(self):
        self.__full_config['system'] = self.__system_info
        self.__full_config['vlan'] = self.get_vlans

        return self.__full_config

    def get_port_list(self, line):
        """
        Create a set() with ports found in line, Ports must be in the STACKID/SLOT/PORT format.
        :param line: line with tagged or untagged ports
        :return: a list() of ports
        """
        ports = set()
        match = re.findall(r'(\d+\/\d\/\d+)', line.lstrip())
        for vlan in match:
            ports.add(vlan)

        pools = re.findall(r'(\S+\/\d\/\S+) to (\S+\/\d\/\S+)', line.lstrip())
        for inicio, fim in pools:
            prefixo = re.findall('^(\d+/1/)', inicio)
            inicio = re.findall('\/(\d+)$', inicio)
            fim = re.findall('\/(\d+)$', fim)
            for port in range(int(inicio[0]), int(fim[0]) + 1):
                ports.add(prefixo[0] + str(port))

        return sorted(list(ports))

    def parse_vlans(self):
        """
        Parse the existing vlan settings in the configuration file
        :return:
        """
        tmp_vlans = []
        try:
            with open(self.file) as running:
                while True:
                    tagged_ports = []
                    untagged_ports = []
                    line = running.readline()

                    if re.match('^vlan', line):
                        # define vlan id and name
                        vlan_id = re.findall('^vlan (\d*)', line)[0]
                        vlan_name = re.findall('name (\w*\S)', line)
                        if len(vlan_name) == 1:
                            vlan_name = vlan_name[0]
                        else:
                            vlan_name = ''

                        # checks if the vlan has tagged ports
                        tag = running.readline()
                        if re.match('^ tagged', tag):
                            tagged_ports = self.get_port_list(tag)

                        # checks if the vlan has untagged ports
                        untag = running.readline()
                        if re.match('^ untagged', untag):
                            untagged_ports = self.get_port_list(untag)

                        tmp_vlans.append({'vlan_id': vlan_id, 'vlan_name': vlan_name, 'tagged_ports': tagged_ports,
                                          'untagged_ports':
                                              untagged_ports})

                    if line == '':
                        break
        except:
            raise

        return tmp_vlans

    def parse_system_info(self):
        try:
            with open(self.file) as running:
                while True:
                    line = running.readline()

                    if line.startswith('ver '):
                        version = re.match('^ver (.*)', line).groups()[0]
                    elif line.startswith('hostname '):
                        hostname = re.match('^hostname (.*)', line).groups()[0]
                    elif line.startswith('ip address '):
                        ip_address = re.match('^ip address (.*)', line).groups()[0]
                    elif line.startswith('ip default-gateway '):
                        ip_default_gateway = re.match('^ip default-gateway (.*)', line).groups()[0]

                    if line == '':
                        break
                return {'hostname': hostname, 'version': version, 'ip_address': ip_address, 'ip_defult-gateway':
                    ip_default_gateway}

        except:
            raise
