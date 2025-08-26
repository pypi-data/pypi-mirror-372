class texstr(str):
    """Simplfy writing tex from python."""

    def __mul__(self, other):
        return texstr(self + "*" + other)

    def __add__(self, other):
        return texstr(super().__add__(other))

    def __sub__(self, other):
        return texstr(self + "-" + other)


# Useful functions
rst_math = lambda x: texstr(":math:`" + x + "`")
rst_term = lambda x: texstr(":term:`" + x + "`")
mathrm = lambda x: texstr(r"\mathrm{" + x.replace(" ", r"\ ") + "}")
_ = lambda x: texstr("_{" + str(x) + "}")
pow = (
    lambda x, y=None: texstr(x + "^{" + str(y) + "}")
    if y is not None
    else texstr("^{" + str(x) + "}")
)
bar = lambda x: texstr(r"\overline{" + str(x) + "}")
sum = lambda under, over, inside: texstr(
    r"\sum_{" + under + "}^{" + over + "} " + inside + " "
)
derivative = lambda x, y: texstr(
    r"\frac{\mathrm{d} " + x + r"}{\mathrm{d} " + y + "}"
)
derivative2 = lambda x, y: texstr(
    derivative(x,y) + pow(2)
)
partial_squared_derivative_for_u = lambda x, y: (
    derivative2(x, y) + u2_(y)
)

frac = lambda x, y: texstr(r"\frac{" + str(x) + "}{" + str(y) + "}")
parenthesis = lambda x: texstr(r"\left(" + x + r"\right)")


multiline = lambda *lines: texstr(
    ""
    # r"\begin{multline}"
    + r" \\ ".join(lines)
    # + r"\end{multline}"
)

# Variables part
conc = texstr(r"\chi ")
uncertainty = texstr("u")
u = uncertainty
u_rel = texstr(r"\sigma ")
area = texstr("A")
Volume = texstr("V")
_sample = _(mathrm("sample"))
_blank = _(mathrm("blank"))
_calib = _(mathrm("calib"))
carbon = texstr("C")
u_of = lambda x: u + parenthesis(x)
u2_of = lambda x: u + parenthesis(x) + pow(2)
u_ = lambda x: u + _(x)
u2_ = lambda x: u + _(x) + pow(2)
u_rel_as_frac = lambda x: frac(u_(x), x)

# Real variables (variables that signify something real)
area_sample = area + _sample
area_calib = area + _calib
area_blank = area + _blank
conc_sample = conc + _sample
conc_calib = conc + _calib
conc_blank = conc + _blank
Volume_calib = Volume + _calib
Volume_sample = Volume + _sample
u_calib = u + _calib
calib_factor = texstr(f"f{_calib}")
u_calib_factor = u_of(calib_factor)
u_A_int_sample = u_of(area + _(mathrm("int,") + "sample"))
u_A_int_calib = u_of(area + _(mathrm("int,") + "calib"))
u_vol_sample = u_of(Volume + _(mathrm("sample")))
u_vol_calib = u_of(Volume + _(mathrm("calib")))
u_instrument = u + _(mathrm("instrument"))
u_linearity = u + _(mathrm("linearity"))
u_sampling = u + _(mathrm("sampling"))
u_rel_conc_blank = u_rel + _(mathrm("conc") + "blank")
u_combined = u + conc + _(mathrm("sample"))
u_expanded = texstr("U") + conc + _(mathrm("sample"))
sigma_rel_series = r"\sigma^{\mathrm{rel}}_{\mathrm{series}}"
sigma_blanks = u_rel + _blank
# lod = conc + r"_{D}"
lod = mathrm("LOD")
carbon_number = carbon + _(mathrm("num"))
carbon_response_factor = carbon + _(mathrm("resp"))
mean_crf = bar(carbon) + _(mathrm("resp"))
ecn_contrib = texstr("y")
u_ecn_contrib = u_(ecn_contrib)

# Convert the to uncertainty name squared
# u_2_i = lambda i: (uncertainty + conc + "^2_{\mathrm{" + i + "}}")
u_2_i = lambda i: (uncertainty + parenthesis(conc + _(mathrm(i))) + pow(2))


if __name__ == "__main__":
    print(area * conc)
