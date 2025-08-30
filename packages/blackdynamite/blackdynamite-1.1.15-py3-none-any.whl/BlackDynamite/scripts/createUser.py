#!/usr/bin/python3
# This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.

################################################################
# import getpass
import os
import stat
import psycopg2
import string
import argparse
import getpass
import os
################################################################
from random import randint, choice
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
################################################################


def generatePassword():
    characters = string.ascii_letters + string.digits
    password = "".join(choice(characters) for x in range(randint(8, 16)))
    return password

################################################################


def createUser(user, host):
    connection_params = dict()
    connection_params["user"] = user

    if host is not None:
        connection_params["host"] = host

    if host is None:
        connection_params["host"] = 'localhost'
    connection_params["password"] = getpass.getpass(
        f'{connection_params["user"]}@{host} password: ')

    try:
        connection = psycopg2.connect(**connection_params)
    except Exception as e:
        print(connection_params)
        raise Exception(str(e)+'\n'+'*'*30 +
                        '\ncannot connect to database\n' + '*'*30)

    new_user = input('new login: ')
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    curs = connection.cursor()
    try:
        curs.execute('create user {0}'.format(new_user))

    except Exception as e:
        print(e)

    print('Setting new password')
    curs.execute('grant create on database blackdynamite to {0}'.format(
        new_user))

    password = generatePassword()
    curs.execute('alter role {0} with password \'{1}\' '.format(
        new_user, password))

    fname = '{0}.bd'.format(new_user)
    print('Saving information to {0}'.format(fname))

    try:
        os.remove(fname)
    except Exception:
        pass
    bdconf = open(fname, 'w')
    bdconf.write(f'password = {password}\n')
    bdconf.write(f'host = {connection_params["host"]}')
    bdconf.close()
    os.chmod(fname, stat.S_IREAD)

################################################################


parser = argparse.ArgumentParser(
    description='User creation tool for blackdynamite')
parser.add_argument("--user", type=str,
                    help="name of the admin user",
                    required=True)
parser.add_argument("--host", type=str,
                    help="host to connect where to create the user",
                    default=None)
args = parser.parse_args()
args = vars(args)

new_user = args['user']
host = args['host']
createUser(new_user, host)
