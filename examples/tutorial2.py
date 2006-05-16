"""This program shows the different protections that PyTables offer to
the user in order to insure a correct data injection in tables.

Example to be used in the second tutorial in the User's Guide.

"""

from numarray import *
from tables import *

# Describe a particle record
class Particle(IsDescription):
    name        = StringCol(length=16) # 16-character String
    lati        = IntCol()             # integer
    longi       = IntCol()             # integer
    pressure    = Float32Col(shape=(2,3)) # array of floats (single-precision)
    temperature = FloatCol(shape=(2,3))   # array of doubles (double-precision)

# Another way to describe the columns of a table
Event = {
    "name"        : StringCol(length=16),
    "lati"        : IntCol(),
    "longi"       : IntCol(),
    "pressure"    : Float32Col(shape=(2,3)),
    "temperature" : FloatCol(shape=(2,3)),
    }

# Open a file in "w"rite mode
fileh = openFile("tutorial2.h5", mode = "w")
# Get the HDF5 root group
root = fileh.root
# Create the groups:
for groupname in ("Particles", "Events"):
    group = fileh.createGroup(root, groupname)
# Now, create and fill the tables in Particles group
gparticles = root.Particles
# Create 3 new tables
for tablename in ("TParticle1", "TParticle2", "TParticle3"):
    # Create a table
    table = fileh.createTable("/Particles", tablename, Particle,
                           "Particles: "+tablename)
    # Get the record object associated with the table:
    particle = table.row
    # Fill the table with 257 particles
    for i in xrange(257):
        # First, assign the values to the Particle record
        particle['name'] = 'Particle: %6d' % (i)
        particle['lati'] = i
        particle['longi'] = 10 - i
        ########### Detectable errors start here. Play with them!
        particle['pressure'] = array(i*arange(2*3), shape=(2,4))  # Incorrect
        #particle['pressure'] = array(i*arange(2*3), shape=(2,3))  # Correct
        ########### End of errors
        particle['temperature'] = (i**2)     # Broadcasting
        # This injects the Record values
        particle.append()
    # Flush the table buffers
    table.flush()

# Now, go for Events:
for tablename in ("TEvent1", "TEvent2", "TEvent3"):
    # Create a table in Events group
    table = fileh.createTable(root.Events, tablename, Event,
                           "Events: "+tablename)
    # Get the record object associated with the table:
    event = table.row
    # Fill the table with 257 events
    for i in xrange(257):
        # First, assign the values to the Event record
        event['name']  = 'Event: %6d' % (i)
        event['TDCcount'] = i % (1<<8)   # Correct range
        ########### Detectable errors start here. Play with them!
        #event['xcoord'] = float(i**2)   # Correct spelling
        event['xcoor'] = float(i**2)     # Wrong spelling
        event['ADCcount'] = i * 2        # Correct type
        #event['ADCcount'] = "sss"          # Wrong type
        ########### End of errors
        event['ycoord'] = float(i)**4
        # This injects the Record values
        event.append()
    # Flush the buffers
    table.flush()

# Read the records from table "/Events/TEvent3" and select some
table = root.Events.TEvent3
e = [ p['TDCcount'] for p in table
      if p['ADCcount'] < 20 and 4 <= p['TDCcount'] < 15 ]
print "Last record ==>", p
print "Selected values ==>", e
print "Total selected records ==> ", len(e)
# Finally, close the file (this also will flush all the remaining buffers!)
fileh.close()
