"""
Defines signed distance functions for the MandelBulb and MandelBox,
useful for real-time rendering in a raymarching context.
"""

module Fractal

export estimate_dist, MandelBulb, MandelBox

using LinearAlgebra

"""
MandelBulb

A struct representing a MandelBulb fractal with specific parameters.

# Fields
- `iterations::Int`: Maximum number of iterations to compute.
- `power::Float64`: Power at which to raise the radius. 8 is traditional.
- `escape::Float64`: Escape radius at which a point is outside the object boundary.
"""
struct MandelBulb <: AbstractSDF
    iterations::Int
    power::Float64
    escape::Float64
end

# http://blog.hvidtfeldts.net/index.php/category/mandelbulb/
function estimate_dist(p::Vec3, object::MandelBulb, curMinDist::Float64=Inf)
    # radius and running derivate
    r = 0
    dr = 1

    # copy p to manipulate
    z = p

    iterations = object.iterations
    pow = object.power

    for i in 1:iterations
        # compute vector magnitude and compare to escape bailout
        r = norm(z)
        if r > object.escape
            break
        end

        # get polar coords
        theta = asin(z[3] / r)
        phi = atan(z[2] / z[1])
        dr = ((r ^ (pow-1)) * pow * dr) + 1

        # scale and rotate
        zr = r ^ pow
        theta = theta * pow
        phi = phi * pow

        # get cartesian coords
        z = zr * Vec3(cos(theta) * cos(phi), sin(phi) * cos(theta), sin(theta))
        z += p
    end

    return (0.5 * log(r) * r) / dr
end

struct MandelBox <: AbstractSDF
    iterations::Int
    scale::Float32
end

# http://blog.hvidtfeldts.net/index.php/2011/11/distance-estimated-3d-fractals-vi-the-mandelbox/
function estimate_dist(p::Vec3, object::MandelBox, curMinDist::Float64=Inf)
    dr = 1.0
    r = 0
    
    z = p
    off = p
    iterations = object.iterations
    scale = object.scale

    for i in 1:iterations
        z = box_fold(z)
        z, dr = sphere_fold(z, dr)

        z = scale * z + off
        dr = dr * abs(scale) + 1
    end

    r = norm(z)

    return r / abs(dr)
end

function box_fold(z::Vec3, minFold=-1, maxFold=1)

    # clamp z components to range
    z[1] > maxFold ? zx=  2 - z[1] : zx=z[1]
    z[1] < minFold ? zx= -2 - z[1] : zx=z[1]

    z[2] > maxFold ? zy=  2 - z[2] : zy=z[2]
    z[2] < minFold ? zy= -2 - z[2] : zy=z[2]

    z[3] > maxFold ? zz=  2 - z[3] : zz=z[3]
    z[3] < minFold ? zz= -2 - z[3] : zz=z[3]

    return Vec3(zx, zy, zz)
end

function sphere_fold(z::Vec3, dr::Float64, minrad=0.5, fixedrad=1)
    r2 = dot(z, z)

    if r2 < minrad
        tempr = fixedrad / minrad
        z *= tempr
        dr *= tempr
    elseif r2 < fixedrad
        tempr = fixedrad / r2
        z *= tempr
        dr *= tempr
    end

    return z, dr
end

end # module Fractal

@time estimate_dist([2, 2, 2], MandelBulb(iterations=100, power=8, escape=4))
