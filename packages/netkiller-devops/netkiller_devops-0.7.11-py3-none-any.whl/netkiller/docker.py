# -*- coding: utf-8 -*-
#========================================
# Author: netkiller@msn.com
# Home: https://www.netkiller.cn
# Callsign: BG7NYT
#========================================
import os, sys
import copy
import json
from io import StringIO

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import PreservedScalarString as pss
import logging, logging.handlers
from optparse import OptionParser, OptionGroup


class Common:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.yaml = YAML()


class Dockerfile(Common):
    def __init__(self,namespace:str,context:str=None,target:str=None):
        super().__init__()
        self.namespace = namespace
        self.dockerfile = {}
        self.dockerfile[self.namespace] = []
        self.context = context
        self.target = target

    def label(self, map):
        for key, value in map.items():
            self.dockerfile[self.namespace].append('LABEL %s="%s"' % (key, value))

    def image(self, value,target:str=None):
        if target:
            self.dockerfile[self.namespace].append("FROM %s AS %s" % (value,target))
        else:
            self.dockerfile[self.namespace].append("FROM %s" % value)
        return self

    def env(self, obj):
        if type(obj) == dict:
            for key, value in obj.items():
                self.dockerfile[self.namespace].append("ENV %s %s" % (key, value))
        return self

    def arg(self, obj):
        if type(obj) == dict:
            for key, value in obj.items():
                self.dockerfile[self.namespace].append("ARG %s=%s" % (key, value))
        return self

    def run(self, obj):
        if type(obj) == str:
            self.dockerfile[self.namespace].append("RUN %s" % obj)
        elif type(obj) == list:
            self.dockerfile[self.namespace].append("RUN %s" % " ".join(obj))
        else:
            pass
        return self

    def volume(self, obj):
        if type(obj) == str:
            self.dockerfile[self.namespace].append("VOLUME %s" % obj)
        elif type(obj) == list:
            self.dockerfile[self.namespace].append('VOLUME ["%s"]' % '","'.join(obj))
            # for vol in obj :
            # self.dockerfile.append('VOLUME %s' % vol)
        return self

    def expose(self, obj):
        if type(obj) == str:
            self.dockerfile[self.namespace].append("EXPOSE %s" % obj)
        elif type(obj) == list:
            self.dockerfile[self.namespace].append("EXPOSE %s" % " ".join(obj))
            # for port in obj :
            # self.dockerfile.append('EXPOSE %s' % port)
        return self

    def copy(self, file, to, target:str = None):
        if target:
            self.dockerfile[self.namespace].append("COPY --from=%s %s %s" % (target,file, to))
        else:
            self.dockerfile[self.namespace].append("COPY %s %s" % (file, to))
        return self

    def entrypoint(self, obj):
        if type(obj) == str:
            self.dockerfile[self.namespace].append("ENTRYPOINT %s" % obj)
        elif type(obj) == list:
            self.dockerfile[self.namespace].append("ENTRYPOINT %s" % " ".join(obj))
        else:
            pass
        return self

    def cmd(self, obj):
        if type(obj) == str:
            self.dockerfile[self.namespace].append("CMD %s" % obj)
        elif type(obj) == list:
            self.dockerfile[self.namespace].append("CMD %s" % " ".join(obj))
        else:
            pass
        return self

    def workdir(self, value):
        self.dockerfile[self.namespace].append("WORKDIR %s" % value)
        return self

    def user(self, value):
        self.dockerfile[self.namespace].append("USER %s" % value)
        return self

    def save(self, path=None):
        dirname = os.path.dirname(path)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
            self.logger.info("Create Dockerfile directory %s" % (dirname))
        # os.makedirs( path,exist_ok=True);
        with open(path, "w") as file:
            file.writelines("\r\n".join(self.dockerfile[self.namespace]))
            file.write("\r\n")

        self.logger.info("Dockerfile %s" % path)
        self.logger.debug(self.dockerfile[self.namespace])
        return self

    def debug(self):
        print(self.dockerfile[self.namespace])

    def show(self):
        print("\r\n".join(self.dockerfile[self.namespace]))


class Networks(Common):
    def __init__(self, name=None):
        super().__init__()
        self.networks = {}
        if name:
            self.name = name
        else:
            self.name = "default"
        self.networks[self.name] = {}

    def enable_ipv6(self, value):
        self.networks[self.name]["enable_ipv6"] = value
        return self

    def driver(self, name="bridge"):
        self.networks[self.name]["driver"] = name
        return self

    def driver_opts(self, value):
        self.networks[self.name]["driver_opts"] = value
        return self

    def ipam(self):
        return self.Ipam(self.networks[self.name])

    class Ipam:
        def __init__(self, obj):
            self.networks = obj
            self.networks["ipam"] = {}

        def driver(self, name="default"):
            self.networks["ipam"]["driver"] = name
            return self

        def config(self, array):
            self.networks["ipam"]["config"] = array
            return self


class Volumes(Common):
    def __init__(self, name="None"):
        super().__init__()
        self.volumes = {}
        if name:
            self.volumes[name] = None

    def ls(self):
        pass

    def create(self, name):
        self.volumes[name] = None
        return self


class Services(Common):
    def __init__(self, name):
        super().__init__()
        self.service = {}
        self.name = name
        self.service[self.name] = {}
        self.dockerfile = None
        self.container_name(self.name)

    def build(self, obj):
        if not "build" in self.service[self.name].keys():
            self.service[self.name]["build"] = {}
        if isinstance(obj, Dockerfile):
            self.service[self.name]["build"] = {
                "context": ".",
                "dockerfile": "Dockerfile"
                # "target": "dev",
            }
            if obj.target :
                self.service[self.name]["build"]["target"] = obj.target
            self.dockerfile = obj
        elif type(obj) == dict:
            self.service[self.name]["build"] = obj
        else:
            self.service[self.name]["build"] = {
                "context": ".",
                "dockerfile": "Dockerfile",
                # "target": "dev",
            }
        return self

    def image(self, name):
        self.service[self.name]["image"] = name
        return self

    def container_name(self, name=None):
        if not name:
            name = self.name
        self.service[self.name]["container_name"] = name
        return self

    def restart(self, value="always"):
        self.service[self.name]["restart"] = value
        return self

    def hostname(self, value="localhost.localdomain"):
        if type(value) == str:
            self.service[self.name]["hostname"] = value
        return self

    def extra_hosts(self, obj):
        if not "extra_hosts" in self.service[self.name].keys():
            self.service[self.name]["extra_hosts"] = []
        if type(obj) == str:
            self.service[self.name]["extra_hosts"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["extra_hosts"].extend(obj)
        else:
            self.service[self.name]["extra_hosts"] = obj
        return self

    def environment(self, obj):
        if not "environment" in self.service[self.name].keys():
            self.service[self.name]["environment"] = []
        if type(obj) == str:
            self.service[self.name]["environment"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["environment"].extend(obj)
        elif type(obj) == dict:
            for key, value in obj.items():
                self.service[self.name]["environment"].append(f"{key}={value}")
        else:
            self.service[self.name]["environment"] = obj
        return self

    def env_file(self, obj):
        if not "env_file" in self.service[self.name].keys():
            self.service[self.name]["env_file"] = []
        if type(obj) == str:
            self.service[self.name]["env_file"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["env_file"].extend(obj)
        else:
            self.service[self.name]["env_file"] = obj
        return self

    def ports(self, obj):
        if not "ports" in self.service[self.name].keys():
            self.service[self.name]["ports"] = []
        if type(obj) == str:
            self.service[self.name]["ports"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["ports"].extend(obj)
        else:
            self.service[self.name]["ports"] = obj
        return self

    def dns(self, obj):
        if not "dns" in self.service[self.name].keys():
            self.service[self.name]["dns"] = []
        if type(obj) == str:
            self.service[self.name]["dns"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["dns"].extend(obj)
        return self

    def expose(self, obj):
        if not "expose" in self.service[self.name].keys():
            self.service[self.name]["expose"] = []
        if type(obj) == str:
            self.service[self.name]["expose"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["expose"].extend(obj)
        else:
            self.service[self.name]["expose"] = obj
        return self

    def working_dir(self, dir="/"):
        self.service[self.name]["working_dir"] = dir
        return self

    def volumes(self, array):
        self.service[self.name]["volumes"] = array
        return self

    def networks(self, array):
        self.service[self.name]["networks"] = array
        return self

    def network_mode(self, mode):
        self.service[self.name]["network_mode"] = mode
        return self

    def sysctls(self, obj):
        if not "sysctls" in self.service[self.name].keys():
            self.service[self.name]["sysctls"] = []
        if type(obj) == str:
            self.service[self.name]["sysctls"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["sysctls"].extend(obj)
        else:
            self.service[self.name]["sysctls"] = obj
        return self

    def entrypoint(self, obj):
        if type(obj) == str:
            self.service[self.name]["entrypoint"] = obj
        elif type(obj) == list:
            self.service[self.name]["entrypoint"] = " ".join(obj)
        return self

    def command(self, obj):
        if type(obj) == str:
            self.service[self.name]["command"] = obj
        elif type(obj) == list:
            self.service[self.name]["command"] = " ".join(obj)
        return self

    def depends_on(self, obj):
        if not "depends_on" in self.service[self.name].keys():
            self.service[self.name]["depends_on"] = []
        if isinstance(obj, Services):
            self.service[self.name]["depends_on"].append(obj.name)
        elif type(obj) == str:
            self.service[self.name]["depends_on"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["depends_on"].extend(obj)
        else:
            self.service[self.name]["depends_on"] = obj
        return self

    def links(self, obj):
        if not "links" in self.service[self.name].keys():
            self.service[self.name]["links"] = []
        if isinstance(obj, Services):
            self.service[self.name]["links"].append(obj.name)
        elif type(obj) == str:
            self.service[self.name]["links"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["links"].extend(obj)
        else:
            self.service[self.name]["links"] = obj
        return self

    def depends_on_object(self, obj):
        if isinstance(obj, Services):
            self.service[self.name]["depends_on"].append(obj.name)
        elif type(obj) == list:
            depends = []
            if isinstance(obj[0], Services):
                for o in obj:
                    depends.append(o.name)
                self.service[self.name]["depends_on"] = depends

    def logging(self, driver="json-file", options=None):
        self.service[self.name]["logging"] = {"driver": driver}
        if options:
            self.service[self.name]["logging"].update({"options": options})
        return self

    def privileged(self, status=True):
        self.service[self.name]["privileged"] = status

    def user(self, value):
        self.service[self.name]["user"] = value
        return self

    def healthcheck(self, value):
        self.service[self.name]["healthcheck"] = value
        return self
    def security_opt(self, obj):
        if not "security_opt" in self.service[self.name].keys():
            self.service[self.name]["security_opt"] = []
        if type(obj) == str:
            self.service[self.name]["security_opt"].append(obj)
        elif type(obj) == list:
            self.service[self.name]["security_opt"].extend(obj)
        elif type(obj) == dict:
            for key, value in obj.items():
                self.service[self.name]["security_opt"].append(f"{key}={value}")
        else:
            self.service[self.name]["security_opt"] = obj
        return self
    def file(self, filename, text):
        dirname = os.path.dirname(filename)
        try:
            if not os.path.isdir(dirname):
                os.makedirs(dirname)
                self.logger.info("Create directory %s" % dirname)
            with open(filename, "w") as file:
                file.writelines(text)
                self.logger.info("Create file %s" % filename)
            return filename
        except Exception as err:
            self.logger.error(f"Create file {filename} {repr(err)}")
        return None

    def dump(self):
        self.yaml.dump(self.service[self.name], sys.stdout)
        # self.logger.debug(yaml)
    def show(self):
        stream = StringIO()
        self.yaml.dump(self.service[self.name], stream)
        yml = stream.getvalue()
        print(yml)

    def debug(self):
        print(self.service)


class Composes(Common):
    compose = {}
    daemon = False
    basedir = "."
    files = {}

    def __init__(self, name):
        super().__init__()
        self.compose = {}
        self.name = name
        self.compose["services"] = {}
        self.dockerfile = {}
        # self.context = 'default'
        self.context = None
        self.environ = None
        self.projectName = None
        self.envFile = None
        self.files = {}

    def env(self, default):
        # if not self.environ :
        self.environ = default
        self.logger.info("%s %s %s" % ("-" * 20, " environment", "-" * 20))
        self.logger.info("%s: %s" % (self.name, self.environ))
        self.logger.info("-" * 50)
        return self

    def env_file(self, file):
        self.envFile = file

    def project_name(self, name):
        self.projectName = name

    def version(self, version):
        self.compose["version"] = str(version)
        return self

    def services(self, obj):
        if isinstance(obj, Services):
            if obj.dockerfile:
                self.dockerfile[obj.name] = obj.dockerfile
                build = {}
                if obj.dockerfile.context:
                    build["context"] = obj.dockerfile.context
                else:
                    build["context"] = os.getcwd()
                build["dockerfile"] = f"{obj.dockerfile.context}/Dockerfile"
                obj.build(build)
            service = copy.deepcopy(obj.service)
            self.compose["services"].update(service)
        return self

    def networks(self, obj):
        self.compose["networks"] = copy.deepcopy(obj.networks)
        return self

    def volumes(self, obj):
        self.compose["volumes"] = copy.deepcopy(obj.volumes)
        return self

    def file(self, filename, text):
        self.files[filename]=text
        return self

    def debug(self):
        # jsonformat = json.dumps(
        #     self.compose, sort_keys=True, indent=4, separators=(",", ":")
        # )
        # return jsonformat
        print(self.compose)

    def dump(self):
        self.yaml.dump(self.compose, sys.stdout)

    def show(self):
        stream = StringIO()
        self.yaml.dump(self.compose, stream)
        yml = stream.getvalue()
        print(yml)

    def filename(self):
        return self.basedir + "/" + self.name + "/" + "compose.yaml"
    def mkdirs(self, filepath):
        dirname = os.path.dirname(filepath)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
            self.logger.info("Create directory %s" % (dirname))

    def save(self, filename=None):

        for filepath, content in self.files.items():
            dirname = os.path.dirname(filepath)
            try:
                if not os.path.isdir(dirname):
                    os.makedirs(dirname)
                    self.logger.info("Create directory %s" % dirname)
                with open(filepath, "w") as file:
                    file.writelines(content)
                    self.logger.info("Create file %s" % filepath)

            except Exception as e:
                self.logger.error(f"Create file {filepath} {repr(e)}")

        if not filename:
            filename = self.filename()

        self.mkdirs(filename)

        try:
            for service, dockerfile in self.dockerfile.items():
                filepath = f"{self.basedir}/{self.name}/{service}/Dockerfile"
                # filepath = self.compose['services'][service]['build']['dockerfile']
                self.mkdirs(filepath)
                dockerfile.save(filepath)
                self.compose['services'][service]['build']['dockerfile']=filepath
                # self.logger.debug("Dockerfile")

            file = open(filename, "w")
            self.yaml.dump(self.compose, stream=file)
            self.logger.info("Save compose file %s" % (filename))
        except Exception as e:
            self.logger.error(e)
            print(e)
            exit()
        return self

    def daemon(self, daemon=True):
        self.daemon = daemon
        return self

    def ls(self):
        command = self.__command("ls")
        self.execute(command)
        return self

    def up(self, service=""):
        self.save()
        d = ""
        if self.daemon:
            d = "-d"
        command = self.__command(
            "up {daemon} {service} --remove-orphans".format(daemon=d, service=service)
        )
        self.execute(command)
        return self

    def down(self, service=""):
        command = self.__command("down {service}".format(service=service))
        self.execute(command)
        return self

    def rm(self, service=""):
        command = self.__command("rm {service}".format(service=service))
        self.execute(command)
        return self

    def restart(self, service=""):
        command = self.__command("restart {service}".format(service=service))
        self.execute(command)
        return self

    def start(self, service=""):
        command = self.__command("start {service}".format(service=service))
        self.execute(command)
        return self

    def stop(self, service=""):
        command = self.__command("stop {service}".format(service=service))
        self.execute(command)
        return self

    def stop(self, service=""):
        command = self.__command("stop {service}".format(service=service))
        self.execute(command)
        return self

    def ps(self, service=""):
        command = self.__command("ps {service}".format(service=service))
        self.execute(command)
        return self

    def top(self, service=""):
        command = self.__command("top {service}".format(service=service))
        self.execute(command)
        return self

    def images(self, service=""):
        command = self.__command("images {service}".format(service=service))
        self.execute(command)
        return self

    def logs(self, service="", follow=False):
        tail = ""
        if follow:
            tail = "-f --tail=50"
        command = self.__command(
            "logs {follow} {service}".format(follow=tail, service=service)
        )
        self.execute(command)
        return self

    def exec(self, service, cmd):
        command = self.__command(
            "exec {service} {cmd}".format(service=service, cmd=cmd)
        )
        self.execute(command)
        return self

    def kill(self, service):
        command = self.__command("kill {service}".format(service=service))
        self.execute(command)
        return self

    def workdir(self, path):
        os.makedirs(path, exist_ok=True)
        self.basedir = path
        self.logger.info("working dir is " + self.basedir)
        return self

    def context(self, value):
        self.context = value
        return self

    def build(self, service=""):
        command = self.__command("build {service}".format(service=service))
        self.execute(command)
        return self

    def __command(self, cmd):
        command = []
        command.append("docker compose")
        if self.projectName:
            command.append("--project-name %s" % self.projectName)
        if self.envFile:
            command.append("--env-file %s" % self.envFile)
        if self.context:
            command.append("‐‐context %s" % self.context)
        command.append("-f {compose}".format(compose=self.filename()))
        command.append(cmd)
        return " ".join(command)

    def execute(self, command):
        self.save()
        self.logger.debug(f"execute {command}")
        if self.environ:
            self.logger.debug("set %s" % self.environ)
            os.environ.update(self.environ)

        self.logger.debug(command)
        code = os.system(command)

        if self.environ:
            for key in self.environ.keys():
                # os.unsetenv(key)
                del os.environ[key]
            # os.environ.clear()
            self.logger.debug("unset %s" % self.environ)
        self.logger.debug("exit %d", code)
        return code


class Docker(Common):
    def __init__(self, env=None):
        super().__init__()
        self.composes = {}
        self.daemon = False
        self.workdir = "/var/tmp/devops"
        self.environ = None

        usage = "usage: %prog [options] up|rm|start|stop|restart|logs|top|images|exec <service>"
        self.parser = OptionParser(usage)
        self.parser.add_option(
            "", "--debug", action="store_true", dest="debug", help="debug mode"
        )
        self.parser.add_option(
            "-e",
            "--environment",
            dest="environment",
            help="environment",
            metavar="development|testing|production",
        )
        self.parser.add_option(
            "-d", "--daemon", dest="daemon", action="store_true", help="run as daemon"
        )
        self.parser.add_option(
            "", "--logfile", dest="logfile", help="logs file.", default="debug.log"
        )
        self.parser.add_option(
            "-l",
            "--list",
            dest="list",
            action="store_true",
            help="print service of environment",
        )
        self.parser.add_option(
            "-f",
            "--follow",
            dest="follow",
            action="store_true",
            default=True,
            help="following logging",
        )
        self.parser.add_option(
            "-c",
            "--compose",
            dest="compose",
            action="store_true",
            help="show docker compose",
        )
        self.parser.add_option(
            "",
            "--export",
            dest="export",
            action="store_true",
            help="export docker compose",
        )
        self.parser.add_option(
            "-b",
            "--build",
            dest="build",
            action="store_true",
            help="build docker image",
        )
        self.parser.add_option(
            "", "--local", dest="local", action="store_true", help="local docker"
        )
        (self.options, self.args) = self.parser.parse_args()
        if self.options.daemon:
            self.daemon = True
        if self.options.debug:
            logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
        elif self.options.logfile:
            logging.basicConfig(
                level=logging.NOTSET,
                format="%(asctime)s %(levelname)-8s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                filename=self.options.logfile,
                filemode="a",
            )

        if self.options.debug:
            print("===================================")
            print(self.options, self.args)
            print("===================================")
        self.logger.debug("=" * 50)
        self.logger.debug(self.options)
        self.logger.debug(self.args)
        self.logger.debug("=" * 50)
        self.logger.debug("logfile: %s" % self.options.logfile)

        if env:
            self.env(env)

    def none(self):
        cmd = "docker images|grep none|awk '{print $3}'|xargs -r docker rmi -f > /dev/null 2>&1"
        os.system(cmd)
        return self

    def env(self, default):
        # if not self.environ :
        self.environ = default
        self.logger.info(
            "%s %s %s" % ("-" * 10, "default environment variable", "-" * 10)
        )
        self.logger.info(self.environ)
        self.logger.info("-" * 50)
        return self

    def workdir(self, path):
        self.workdir = path

    def environment(self, compose):
        if self.options.local:
            compose.env(None)
        elif self.environ:
            compose.env(self.environ)
            self.logger.info("Override [%s] environ: %s" % (compose.name, self.environ))
        compose.workdir(self.workdir)
        # print(compose.dump())
        self.composes[compose.name] = compose
        self.logger.info("Add environment: %s" % (compose.name))
        return self

    def sysctl(self, conf):
        self.logger.info("-" * 50)
        for name, value in conf.items():
            cmd = "sysctl -w {name}={value}".format(name=name, value=value)
            self.logger.info(cmd)
            os.system(cmd)
        self.logger.info("-" * 50)
        return self

    def ls(self):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.ls()
        else:
            for env, obj in self.composes.items():
                obj.ls()
        return self

    def up(self, service=""):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            if self.daemon:
                composes.daemon().up(service)
            else:
                composes.up(service)
        else:
            for env, obj in self.composes.items():
                if self.daemon:
                    obj.daemon().up(service)
                else:
                    obj.up(service)
        return self

    def rm(self, service=""):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.rm(service)
        else:
            for env, obj in self.composes.items():
                obj.rm(service)
        return self

    def down(self, service=""):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.down(service)
        else:
            for env, obj in self.composes.items():
                obj.down(service)
        return self

    def start(self, service=""):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.start(service)
        else:
            for env, obj in self.composes.items():
                obj.start(service)
        return self

    def stop(self, service=""):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.stop(service)
        else:
            for env, obj in self.composes.items():
                obj.stop(service)
        return self

    def restart(self, service=""):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.restart(service)
        else:
            for env, obj in self.composes.items():
                obj.restart(service)
        return self

    def ps(self, service=""):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.ps(service)
        else:
            for env, obj in self.composes.items():
                obj.ps(service)
        return self

    def top(self, service=""):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.top(service)
        else:
            for env, obj in self.composes.items():
                obj.top(service)
        return self

    def images(self, service=""):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.images(service)
        else:
            for env, obj in self.composes.items():
                obj.images(service)
        return self

    def logs(self, service="", follow=False):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.logs(service, follow)
        else:
            for env, obj in self.composes.items():
                obj.logs(service, follow)
        return self

    def list(self):
        self.logger.debug("-" * 50)
        if self.options.environment and self.options.environment in self.composes:
            print(
                "%s: %s"
                % (
                    self.options.environment,
                    self.composes[self.options.environment].environ or "",
                )
            )
            services = self.composes[self.options.environment].compose["services"]
            for service in services:
                print(" " * 4, service)
        else:
            for env, obj in self.composes.items():
                print("%s: %s" % (env, obj.environ or ""))
                for service in obj.compose["services"]:
                    print(" " * 4, service)
        exit()

    def build(self, service):
        self.logger.info("build " + self.service)
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.build(service)
        else:
            for env, value in self.composes.items():
                value.build(service)

    def dump(self):
        if self.options.environment and self.options.environment in self.composes:
            compose = self.composes[self.options.environment]
            compose.dump()
        else:
            for env, compose in self.composes.items():
                print(f"---------- {env} ----------")
                if compose:
                    print(compose.dump())

    def save_all(self):
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.save(self.options.environment + ".yaml")
        else:
            for filename, value in self.composes.items():
                value.save(filename + ".yaml")

    def exec(self, service, array):
        cmd = " ".join(array)
        if self.options.environment and self.options.environment in self.composes:
            composes = self.composes[self.options.environment]
            composes.exec(service, cmd)
        else:
            for env, obj in self.composes.items():
                obj.exec(service, cmd)

    def usage(self):
        print("Python controls the docker manager.")
        self.parser.print_help()
        print(
            "\nHomepage: http://www.netkiller.cn\tAuthor: Neo <netkiller@msn.com>\nHelp: https://github.com/netkiller/devops/blob/master/doc/docker.md"
        )
        exit()

    def main(self):
        if self.options.compose:
            self.dump()
            exit()

        # if not self.options.environment and len(self.composes) > 1:
        #     self.list()

        if self.options.export:
            self.save_all()
            exit()

        if self.options.list:
            self.list()

        if self.options.build:
            self.service = " ".join(self.args)
            self.build(self.service)
            exit()

        if self.options.environment:
            if not self.args:
                self.list()

            if len(self.args) > 1:
                self.service = " ".join(self.args[1:2])
            else:
                self.service = ""
            self.logger.debug("service: " + self.service)

            if self.args[0] == "ls":
                self.ls()
            elif self.args[0] == "up":
                self.up(self.service)
            elif self.args[0] == "down":
                self.down(self.service)
                self.logger.info("down " + self.service)
            elif self.args[0] == "rm":
                self.rm(self.service)
                self.logger.info("rm " + self.service)
            elif self.args[0] == "start":
                self.start(self.service)
                self.logger.info("start " + self.service)
            elif self.args[0] == "stop":
                self.stop(self.service)
                self.logger.info("stop " + self.service)
            elif self.args[0] == "restart":
                self.restart(self.service)
                self.logger.info("restart" + self.service)
            elif self.args[0] == "ps":
                self.ps(self.service)
            elif self.args[0] == "top":
                self.top(self.service)
            elif self.args[0] == "images":
                self.images(self.service)
            elif self.args[0] == "logs":
                self.logs(self.service, self.options.follow)
            elif self.args[0] == "exec":
                self.exec(self.service, self.args[2:])
            else:
                self.usage()
        else:
            self.list()
