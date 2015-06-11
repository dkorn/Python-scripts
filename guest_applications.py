#!/usr/bin/python

# Usage: $ sudo python guest_applications.py 1

# Grant permission in vmdb_:
# 1. GRANT ALL PRIVILEGES ON TABLE guest_applications TO root;
# 2. GRANT USAGE, SELECT ON SEQUENCE guest_applications_id_seq TO root;

import psycopg2
import subprocess
import sys


USER = 'root'
PASSWORD = 'smartvm'
DB_NAME = 'vmdb_development'
DOCKER_IMAGE = 'docker.io/fedora'


# Try to connect to db
try:
    conn = psycopg2.connect("dbname={0} user={1} password={2}".
                            format(DB_NAME, USER, PASSWORD))
except:
    print("ERROR: Unable to connect to the {0}.".format(DB_NAME))

# Open a cursor to perform database operations
cur = conn.cursor()

# Run bash command to retrieve guest applications from docker.io/fedora image
p = subprocess.Popen(['docker', 'run', DOCKER_IMAGE, 'rpm', '-qa', '--qf',
                      '%{NAME} %{VERSION} %{RELEASE} %{ARCH}\n'],
                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = p.communicate()

lines = out.split('\n')

del lines[-1]

for line in lines:
    values = line.split()

    # Insert relevant data into guest_applications table
    cur.execute("INSERT INTO guest_applications "
                "(name, version, release, arch, container_image_id) "
                "VALUES (%s, %s, %s, %s, %s)",
                (values[0], values[1], values[2], values[3], sys.argv[1]))

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()
