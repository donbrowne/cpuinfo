import os.path


def read_file(path):
    """Return the contents of the specified file"""
    with open(path, "r") as f:
        return f.read()

SYS_PATH = "/sys/devices/system/"
CPU_PATH = os.path.join(SYS_PATH, "cpu")
CPU0_PATH = os.path.join(CPU_PATH, "cpu0")
cpu_id_folder_path = lambda id: os.path.join(CPU_PATH, "cpu%s" % id)
node_id_folder_path = lambda id: os.path.join(SYS_PATH, "node", "node%s" % id)

cpus = 0
nodes = 0
cpu_path = cpu_id_folder_path(cpus)
node_path = node_id_folder_path(nodes)
cores = set()
sockets = set()

# Slice to get rid of trailing \n
online_cpus = read_file(os.path.join(CPU_PATH, "online"))[:-1]
max_freq = read_file(os.path.join(CPU0_PATH, "cpufreq", "cpuinfo_max_freq"))[:-1]
min_freq = read_file(os.path.join(CPU0_PATH, "cpufreq", "cpuinfo_min_freq"))[:-1]
max_freq = int(max_freq) / 1000
min_freq = int(min_freq) / 1000

intel_turbo_path = os.path.join(SYS_PATH, "intel_pstate", "no_turbo")
if os.path.isfile(intel_turbo_path):
    with open(intel_turbo_path, "r") as f:
        turbo_disabled = int(f.read())
        intel_turbo = "off" if turbo_disabled else "on"
else:
    intel_turbo = "unsupported"

while os.path.isdir(cpu_path):
    core_id_path = os.path.join(cpu_path, "topology", "core_id")
    socket_id_path = os.path.join(cpu_path, "topology", "physical_package_id")

    with open(socket_id_path, "r") as f:
        sockets.add(f.read())

    with open(core_id_path, "r") as f:
        cores.add(f.read())

    cpus += 1
    cpu_path = cpu_id_folder_path(cpus)

while os.path.isdir(node_path):
    nodes += 1
    node_path = node_id_folder_path(nodes)

info = dict(logical_cores=cpus, physical_cores=len(cores), sockets=len(sockets),
            numa_nodes=nodes, cores_per_socket=(len(cores) / len(sockets)),
            threads_per_socket=(cpus / len(cores)), intel_turbo=intel_turbo,
            online_cpus=online_cpus, max_freq=max_freq, min_freq=min_freq
            )
print info
