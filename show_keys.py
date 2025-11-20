from skyfield.api import load

eph = load('de441.bsp')

print("Supported targets:")
for name in eph.names():
    print(" -", name)
