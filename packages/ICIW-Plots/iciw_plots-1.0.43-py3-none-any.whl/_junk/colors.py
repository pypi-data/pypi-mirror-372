import colorsys

base_H, L, S = colorsys.rgb_to_hls(217 / 256, 68 / 256, 38 / 256)
base_H *= 360
L *= 100
S *= 100
print(base_H, L, S)
for i in [-30, -15, 0, 15, 30]:
    print(base_H + i)
    H = (base_H + i) % 360
    print(H)
    print(colorsys.hls_to_rgb(H / 360, L / 100, S / 100))
