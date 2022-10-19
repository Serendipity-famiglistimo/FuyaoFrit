import ghpythonlib.components as ghcomp
import Rhino.Geometry as rg
v2, _ = ghcomp.Rotate([rg.Vector3d(1, 0, 0)], ghcomp.Pi(-1/3), rg.Point3d(0, 0, 0))
print(v2)
v3, _ = ghcomp.Rotate([rg.Vector3d(1, 0, 0)], ghcomp.Pi(-0.3333), rg.Point3d(0, 0, 0))

print(v3)