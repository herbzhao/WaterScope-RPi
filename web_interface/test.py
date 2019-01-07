

@classmethod
def auto_focus(cls):
        
    def gss(f, a, b, tolerance):
        """     Golden section search.

        Algorithm for finding the interval within which the mode (focus point) lies,
        minimizing the number of function (focus_measure) evaluations.

        We start with an interval [a,b]=[zmin,zmax] and return an interval [c,d] such
        that d-c<=tol=sweep_threshold.

        https://en.wikipedia.org/wiki/Golden-section_search """

        (a,b)=(min(a,b),max(a,b))
        h = b - a
        if h <= tolerance: return (a,b)

        # required steps to achieve tolerance
        n = int(math.ceil(math.log(tolerance/h)/math.log(invphi)))

        c = a + invphi2 * h
        d = a + invphi * h
        yc = f(c)
        yd = f(d)

        for k in np.xrange(n-1):
            if yc < yd:
                b = d
                d = c
                yd = yc
                h = invphi*h
                c = a + invphi2 * h
                yc = f(c)
            else:
                a = c
                c = d
                yc = yd
                h = invphi*h
                d = a + invphi * h
                yd = f(d)

        if yc < yd:
            return (a,d)
        else:
            return (c,b)

    def move_stage_to(z):
        # move to the absolute z
        cls.current_z = 'a'
        move_stage(deltaZ)

    def focus_measure_at_z(z):
        move_stage_to_z(z)
        focus_value =  
        return focus_value

    # coarse scan using gss
    (sweep_start, sweep_end) = gss(focus_measure_at_z, zmin, zmax, sweep_threshold)

    # fine sweep - existing code?