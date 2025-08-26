# -*- coding: utf-8 -*-
#
# This file is part of the bliss project
#
# Copyright (c) 2015-2023 Beamline Control Unit, ESRF
# Distributed under the GNU LGPLv3. See LICENSE for more info.
import socket
import weakref

import gevent
from gevent import monkey

import paramiko
from paramiko.ssh_exception import SSHException
from paramiko import pipe as paramiko_pipe
from gevent import select, queue, lock

from bliss import global_map
from bliss.common.cleanup import error_cleanup

from .exceptions import CommunicationError, CommunicationTimeout


class SshCommandTimeout(CommunicationTimeout):
    """Command timeout error"""


class SshCommand:
    class Error:
        pass

    class Transaction:
        def __init__(self, ssh_command, transaction, clear_transaction=True):
            self.__ssh_command = ssh_command
            self.__transaction = transaction
            self.__clear_transaction = clear_transaction
            self._data = b""

        def __enter__(self):
            return self

        def __exit__(self, *args):
            cmd = self.__ssh_command
            with cmd._lock:
                try:
                    trans_index = cmd._transaction_list.index(self.__transaction)
                except ValueError:
                    return

                if trans_index == 0:
                    while not self.__transaction.empty():
                        read_value = self.__transaction.get()
                        if not isinstance(
                            read_value, (SSHException, CommunicationError)
                        ):
                            self.data += read_value
                    if self.__clear_transaction and len(cmd._transaction_list) > 1:
                        cmd._transaction_list[1].put(self.data)
                    else:
                        self.__transaction.put(self.data)

                if self.__clear_transaction:
                    cmd._transaction_list.pop(trans_index)

    def __init__(
        self,
        hostname,
        username,
        password,
        remote_command,
        eol=b"\n",
        timeout=5.0,
        connection_cbk=None,
    ):
        """
        Class to run remotely through ssh a command that get input from stdin
        and returns message through stdout and stderr

        @params hostname the remote hostname
        @params username the login name use to connect on the remote machine
        @params password the login's password
        @params eol the default end of line use by readline
        @params timeout the default timeout use to read and write
        @params connection_cbk sometime on connection you need to purge a banner and
        configure the remote executable when it starts. so the callback connection take this object
        as parameter
        """
        self._hostname = hostname
        self._username = username
        self._password = password
        self._remote_command = remote_command
        self._eol = eol
        self._timeout = timeout
        self._connection_cbk = connection_cbk

        self._chan = None

        self._raw_read_task = None
        self._transaction_list = []
        self._lock = lock.RLock()
        self._external_lock = lock.RLock()
        self._ssh = paramiko.SSHClient()
        self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        global_map.register(self, parents_list=["comms"], tag=str(self))

    @property
    def lock(self):
        return self._external_lock

    def connect(self):
        if self._raw_read_task is None:
            if not self._ssh._transport or not self._ssh._transport.active:
                socket_klass = monkey.get_original("socket", "socket")
                sock = socket_klass(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((self._hostname, 22))

                self._ssh.connect(
                    self._hostname,
                    username=self._username,
                    password=self._password,
                    allow_agent=False,
                    sock=sock,
                )

            chan = self._ssh._transport.open_session(timeout=None)
            chan.setblocking(False)
            chan.exec_command(self._remote_command)

            # should use fileno from chan but mixed pipe for
            # stderr and stdout and causes problem with event
            # so create on pipe for each
            # code adapted from chan.fileno
            stdout_pipe = paramiko_pipe.make_pipe()
            stderr_pipe = paramiko_pipe.make_pipe()
            chan._pipe = stdout_pipe
            chan.in_buffer.set_event(stdout_pipe)
            chan.in_stderr_buffer.set_event(stderr_pipe)

            self._chan = chan

            self._raw_read_task = gevent.spawn(
                self._raw_read,
                weakref.proxy(self),
                weakref.proxy(chan),
                stdout_pipe.fileno(),
                stderr_pipe.fileno(),
            )
            if self._connection_cbk:
                self._connection_cbk(self)
        return True

    def close(self):
        self._ssh.close()

    def write(self, msg):
        return self._write(msg, create_transaction=False)

    def write_read(self, msg, size=1, timeout=None):
        transaction = self._write(msg)
        return self._read(transaction, size=size, timeout=timeout)

    def write_readline(self, msg, eol=None, timeout=None):
        timeout = timeout or self._timeout
        with gevent.Timeout(
            timeout, SshCommandTimeout(f"write_readline {msg} timed out")
        ):
            transaction = self._write(msg)
            return self._readline(eol=eol, timeout=timeout, transaction=transaction)

    def write_readlines(self, msg, nb_lines, eol=None, timeout=None):
        timeout = timeout or self._timeout
        with gevent.Timeout(
            timeout,
            SshCommandTimeout("write_readlines(%s,%d) timed out" % (msg, nb_lines)),
        ):
            transaction = self._write(msg)
            str_list = []
            for i in range(nb_lines):
                clear_transaction = i == nb_lines - 1
                str_list.append(
                    self._readline(
                        eol=eol,
                        timeout=timeout,
                        transaction=transaction,
                        clear_transaction=clear_transaction,
                    )
                )
            return str_list

    def _write(self, msg, transaction=None, create_transaction=True):
        self.connect()  # auto connect
        with self._lock:
            if transaction is None and create_transaction:
                transaction = self.new_transaction()
            with error_cleanup(self._pop_transaction, transaction=transaction):
                size_to_send = len(msg)
                already_sent = 0
                # print('_write',msg)
                while size_to_send:
                    send_size = self._chan.send(msg[already_sent:])
                    if not send_size:
                        break  # channel closed
                    size_to_send -= send_size
                    already_sent += send_size

        return transaction

    def _readline(self, transaction, eol=None, timeout=None, clear_transaction=True):
        timeout = timeout or self._timeout
        eol = eol or self._eol
        with SshCommand.Transaction(self, transaction, clear_transaction) as ctx:
            with gevent.Timeout(timeout, SshCommandTimeout("{self._hostname}")):
                if not isinstance(eol, bytes):
                    eol = eol.encode()
                ctx.data = b""
                eol_pos = -1
                while eol_pos == -1:
                    read_value = transaction.get()
                    if isinstance(read_value, (SSHException, CommunicationError)):
                        raise read_value
                    ctx.data += read_value
                    eol_pos = ctx.data.find(eol)
                msg = ctx.data[:eol_pos]
                ctx.data = ctx.data[eol_pos + len(eol) :]
        return msg

    def _read(self, transaction, size=1, timeout=None, clear_transaction=True):
        timeout = timeout or self._timeout
        with SshCommand.Transaction(self, transaction, clear_transaction) as ctx:
            with gevent.Timeout(timeout, SshCommandTimeout("{self._hostname}")):
                ctx.data = b""

                while len(ctx.data) < size:
                    read_value = transaction.get()
                    if isinstance(read_value, (SSHException, CommunicationError)):
                        raise read_value
                    ctx.data += read_value
                msg = ctx.data[:size]
                ctx.data = ctx.data[size:]
        return msg

    def new_transaction(self):
        data_queue = queue.Queue()
        self._transaction_list.append(data_queue)
        return data_queue

    def _pop_transaction(self, transaction=None):
        index = self._transaction_list.index(transaction)
        self._transaction_list.pop(index)

    @staticmethod
    def _raw_read(ssh_command, chan, stdout_pipe, stderr_pipe):
        try:
            while True:
                r, w, e = select.select([stderr_pipe, stdout_pipe], [], [])
                if r:
                    error_str = None
                    if stderr_pipe in r:
                        error_str = chan.recv_stderr(16 * 1024)
                        print("ERROR", error_str)
                        with ssh_command._lock:
                            if ssh_command._transaction_list:
                                ssh_command._transaction_list[0].put(
                                    CommunicationError(error_str)
                                )

                    std_str = None
                    if stdout_pipe in r:
                        std_str = chan.recv(16 * 1024)
                        # print("std_str",std_str)

                    with ssh_command._lock:
                        if not error_str and not std_str and std_str is not None:
                            break  # disconnected
                        elif std_str and ssh_command._transaction_list:
                            ssh_command._transaction_list[0].put(std_str)
        except Exception:
            import traceback

            traceback.print_exc()
            pass
        finally:
            ssh_command._raw_read_task = None
            ssh_command._chan = None
            transaction_list = ssh_command._transaction_list
            chan.close()
            stdout_pipe.close()
            stderr_pipe.close()
            try:
                # inform all pending transaction
                with ssh_command._lock:
                    for trans in transaction_list:
                        trans.put(CommunicationError("Disconnected"))
            except Exception:
                pass
