# bezier.py

class UnitBezier:
    def __init__(self, p1x, p1y, p2x, p2y):
        """
        Initializes a UnitBezier curve with control points.
        :param p1x: X-coordinate of the first control point.
        :param p1y: Y-coordinate of the first control point.
        :param p2x: X-coordinate of the second control point.
        :param p2y: Y-coordinate of the second control point.
        """
        self.cx = 3.0 * p1x
        self.bx = 3.0 * (p2x - p1x) - self.cx
        self.ax = 1.0 - self.cx - self.bx

        self.cy = 3.0 * p1y
        self.by = 3.0 * (p2y - p1y) - self.cy
        self.ay = 1.0 - self.cy - self.by

    def sample_curve_x(self, t):
        """
        Sample the X-coordinate of the curve at time t.
        :param t: Parameter between 0 and 1.
        :return: X-coordinate at the given t.
        """
        return ((self.ax * t + self.bx) * t + self.cx) * t

    def sample_curve_y(self, t):
        """
        Sample the Y-coordinate of the curve at time t.
        :param t: Parameter between 0 and 1.
        :return: Y-coordinate at the given t.
        """
        return ((self.ay * t + self.by) * t + self.cy) * t

    def sample_curve_derivative_x(self, t):
        """
        Sample the derivative of the curve's X-coordinate at time t.
        :param t: Parameter between 0 and 1.
        :return: Derivative of X at the given t.
        """
        return (3.0 * self.ax * t + 2.0 * self.bx) * t + self.cx

    def solve_curve_x(self, x, epsilon=1e-6):
        """
        Solve for t given an x using Newton's method.
        :param x: The X value to solve for.
        :param epsilon: Precision of the solution.
        :return: The corresponding t value.
        """
        t0, t1, t2 = 0.0, 1.0, x
        for _ in range(8):  # Newton's method iterations
            x2 = self.sample_curve_x(t2) - x
            if abs(x2) < epsilon:
                return t2
            d2 = self.sample_curve_derivative_x(t2)
            if abs(d2) < epsilon:
                break
            t2 -= x2 / d2

        # Bisection method
        while t0 < t1:
            x2 = self.sample_curve_x(t2)
            if abs(x2 - x) < epsilon:
                return t2
            if x > x2:
                t0 = t2
            else:
                t1 = t2
            t2 = (t1 - t0) * 0.5 + t0

        return t2

    def solve(self, x, epsilon=1e-6):
        """
        Solve the curve for a given x and return the corresponding y value.
        :param x: The X value to solve for.
        :param epsilon: Precision of the solution.
        :return: The corresponding Y value.
        """
        return self.sample_curve_y(self.solve_curve_x(x, epsilon))


def bezier_progress(a, b, c, d, t):
    """
    Progress through the animation using a bezier curve.
    :param a: X1 of the bezier curve.
    :param b: Y1 of the bezier curve.
    :param c: X2 of the bezier curve.
    :param d: Y2 of the bezier curve.
    :param t: Time value between 0 and 1.
    :return: The resulting progress value based on the bezier curve.
    """
    curve = UnitBezier(a, b, c, d)
    return curve.solve(t)
