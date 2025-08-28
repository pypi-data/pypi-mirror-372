import matplotlib.pyplot as plt
import numpy as np
import ICIW_Plots.cyclers as ICIW_cyclers
import cycler

##
# pip install ICIW-Plots
##

# use the defined stylesheet
plt.style.use(["ICIWstyle"])

plt.figure()
x = np.linspace(-2 * np.pi, 2 * np.pi)
my_green_cycler = ICIW_cyclers.ICIW_colormap_cycler("Greens", 7, start=0.2)
with plt.rc_context({"axes.prop_cycle": my_green_cycler}):
    for i in range(7):
        plt.plot(x, np.sin(x + (i * (4 * np.pi / 7))))
# plt.show()
plt.savefig("cycler.svg")

fig, axs = plt.subplots(2, 2)

x = np.linspace(-10, 10, 100)

# using a monocoloured cycler to auto colour a few similar plots
my_green_cycler = ICIW_cyclers.ICIW_colormap_cycler("Greens", 3, start=0.5)
axs[0, 0].set_prop_cycle(my_green_cycler)
for i in range(3):
    axs[0, 0].plot(x, x**i)
axs[0, 0].set_xlabel(r"$\xi / 1$")

# using an inner product of cyclers to colour groups of similiar plots
my_blue_cycler = ICIW_cyclers.ICIW_colormap_cycler("Blues", 5, stop=0.5)
my_linestyle_cycler = ICIW_cyclers.ICIW_linestyle_cycler(3)

axs[0, 1].set_prop_cycle(my_blue_cycler * my_linestyle_cycler)
for i in range(5):
    for j in range(3):
        axs[0, 1].plot(x, i * x + j * 5)

# using a symbol cycler with user defined symbols and different colors
my_color_cycler = ICIW_cyclers.ICIW_colormap_cycler("viridis", 3)
my_symbol_cycler = ICIW_cyclers.ICIW_symbol_cycler(3, sym_list=["<", ">", "|"])

axs[1, 0].set_prop_cycle(my_symbol_cycler + my_color_cycler)
for i in range(3):
    axs[1, 0].plot(x, x**i, ls=None)

# text at coordinate system
my_custom_cycler = cycler.cycler("color", ["r", "g", "b"])
axs[1, 1].set_prop_cycle(my_custom_cycler)
axs[1, 1].plot(x, x**2)
axs[1, 1].plot(x, x**1.5)
axs[1, 1].plot(x, np.e ** (x / 2))
axs[1, 1].text(0.5, 20, "absolute pos")  # this is at axis coordinates
axs[1, 1].text(0.5, 0.5, "relative pos", transform=axs[1, 1].transAxes)

plt.savefig("test.svg")

plt.show()
