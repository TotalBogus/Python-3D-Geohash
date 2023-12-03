# Python 3D Geohash
 Convert a 3D normalised vector into a geohash (morton key)

 Geohashes (aka morton keys) are a way of mapping a set of multidimensional points (3 in this case) onto a 1D line while still preserving spatial locality i.e. points close together in the original dataset will still be close together on the 1D line.

 This library uses Z-curves to do the actual conversions between 3D space and 1D space. Everything is implemented (almost) exclusively using bitwise operations and hash tables so it is *extremely* fast (>2 million conversions/sec on an intel 13900k)
